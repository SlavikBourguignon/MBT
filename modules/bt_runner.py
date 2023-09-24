import utils
import sys 
sys.path.append('modules/')
import warnings

warnings.filterwarnings("ignore")


from forwardtest import ForwardTest
from vbt_strategies import Strategy as Strat
import  metaparams as mp
import params_parser as pp
import utils, logger
import copy

def run(params):
    paramsData, paramsRun = params['paramsData'],params['paramsRun']
    paramsBT,  paramsPF = params['paramsBT'],params['paramsPF']

    Data, Run, BT, PF = pp.parse(paramsData, paramsRun, paramsBT, paramsPF)
    runTxt, run  = Run

    for dataTxt, data in Data:

        test = ForwardTest(data)
        test.compute_entries_exits(run)

        for btTxt, bt in BT:
            usedKelly = False

            for pfTxt, pf in PF:

                try:
                    paramsTxt = utils.regroupParams(dataTxt, runTxt, btTxt, pfTxt)
                    tried, path = logger.verifyTried(paramsTxt, data, bt, run)
                    
                    if not tried:
                        test.compute_PF(bt, pf)
                        ptf = test.reconstruct_pf()

                        logger.log(paramsTxt, data, run, bt, pf, ptf)

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

                            logger.log(paramsTxt, data, run, bt, pf_kelly, ptf)

                    else: 
                        print('This set of parameter has already been computed.\n'
                            'The results can be found here: \n'
                            f'{path}')
                except Exception as e:
                    utils.debug('There was an issue with the following parameters: ', 
                            'Data: ', data, 
                            'BT: ', bt, 
                            'PF: ',pf,
                            'Got exception: ', e,
                            sep = '\n')