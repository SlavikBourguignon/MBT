import utils
import sys 
sys.path.append('modules/')
import warnings

warnings.filterwarnings("ignore")


from forwardtest import ForwardTest
from vbt_strategies import Strategy as Strat
import metaparams as mp
import params_parser as pp
import utils, logger
import copy
import os, telegram
import decorators as dct
import dotenv, json
import datetime

def handle_arg(arg):
    if isinstance(arg, dict):
        return json.dumps(arg, indent = 4, default = handle_arg)
    
    try :
        return str(arg)
    except:
        return type(arg)

def send_message(start_msg, params, end_msg, e):
    msg = start_msg
    for name_arg, arg in zip(params.keys(), params.values()):
        msg += f'{name_arg}: '
        msg += handle_arg(arg)
        msg += '\n'
        msg += end_msg

    dotenv.load_dotenv()
    token = os.getenv('TOKEN')
    channelId = os.getenv('CHANNEL_ID')
    bot = telegram.Bot(token = token)
    bot.send_message(chat_id = channelId, text = msg)

def send_error_message(params, e):
    start_msg = 'Error on function \n'
    end_msg = f'\nGot exception:\n{e}\n\nProceeding'
    send_message(start_msg, params, end_msg, e)


@dct.telegram_update_backtest
def run(params):
    paramsData, paramsRun = params['paramsData'],params['paramsRun']
    paramsBT,  paramsPF = params['paramsBT'],params['paramsPF']

    Data, Run, BT, PF = pp.parse(paramsData, paramsRun, paramsBT, paramsPF)
    runTxt, run  = Run

    for dataTxt, data in Data:
        
        try : 
            test = ForwardTest(data)
        except Exception as e :
            params = {'function': 'ForwardTest init', 'data': dataTxt}
            send_error_message(params, e)
            continue

        try:
            test.compute_entries_exits(run)
        except Exception as e:
            params = {'function': 'compute_entries_exits ', 'run': runTxt} 
            send_error_message(params, e)
            continue
        firstError = True
        for btTxt, bt in BT:
            usedKelly = False
            
            for pfTxt, pf in PF:

                try:
                    paramsTxt = utils.regroupParams(dataTxt, runTxt, btTxt, pfTxt)
                    tried, path = logger.verifyTried(paramsTxt, data, bt, run)
                    
                    if not tried:
                        test.compute_PF(bt, pf)
                        ptf = test.reconstruct_pf()

                        logger.log(paramsTxt, data, run, bt, pf, ptf, test.entries_list, test.exits_list)
                        try :
                            if not usedKelly:
                                stats = ptf.stats()
                                winrate = stats['Win Rate [%]'] / 100
                                average_win = stats['Avg Winning Trade [%]'] / 100
                                average_loss = abs(stats['Avg Losing Trade [%]'] /100) 
    
                                pf_kelly = copy.deepcopy(pf)
                                kelly_size = test.kelly_criterion(winrate, average_win, average_loss)
                                pf_kelly['size'] = kelly_size

                                test.compute_PF(bt, pf_kelly)
                                ptf = test.reconstruct_pf()
                                
                                usedKelly = True

                                logger.log(paramsTxt, data, run, bt, pf_kelly, ptf, test.entries_list, test.exits_list)
                        except : 
                            pass
                    else: 
                        print('This set of parameter has already been computed.\n'
                            'The results can be found here: \n'
                            f'{path}')
                except Exception as e:
                    params = {'function': 'Backtest computation', 'bt': btTxt, 'pf': pfTxt}
                    if firstError:
                        send_error_message(params, e)
                        firstError = False
                    continue