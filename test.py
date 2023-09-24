import sys 
sys.path.append('modules/')
import warnings

warnings.filterwarnings("ignore")


from forwardtest import ForwardTest
from vbt_strategies import Strategy as Strat
import  metaparams as mp
import params_parser as pp
import utils, logger
import copy, json
import ranking



paramsData = {
        'download_params': {
            'start': '2017-10-1',
            'end': '2023-1-1',
            'symbols': 'BTCUSDT',
            'interval': '1h',
            'show_progress': False   # To print the downloading progress   
        },
        'get_params': {
            'column': ['Close']
        },
}

paramsRun = {
        'strategy_name': 'Trix',
        'inputs': { 
            'ema_window': {'start': 5, 'stop': 20, 'step': 1},
            'signal': {'start': 10, 'stop': 30, 'step': 1},
            'param_product': True
        },
}

paramsBT = {
    'length': {
        'weeks': 10  #durée pendant laquelle on optimise les paramètres
    },
    'forward': {
        'weeks': 5  #durée pendant laquelle on joue les paramètres optimisés
    }, 
    'optimizer': ['!max_drawdown!', '!total_return! - 2 * !max_drawdown!', '!sharpex_ratio!'] 
    #'param_product': True   
}
"""
[ 
'alpha', 'annual_returns', 'annualized_return', 'annualized_volatility','beta','calmar_ratio', 
'cumulative_returns', 'daily_returns', 'deflated_sharpe_ratio', 
'down_capture', 'downside_risk' , 'information_ratio', 'max_drawdown', 'omega_ratio', 
'returns', 'returns_acc', 'returns_stats', 
'sharpe_ratio', 'sortino_ratio', 'tail_ratio', 'to_doc', 
'total_benchmark_return', 'total_profit', 'total_return',
 'value', 'value_at_risk', 'xs']
"""
paramsPF = {
    'fees' : 0.1/100,
    'size_type': 'Percent',
    'size': [0.2, 0.3, 0.4, 0.5], 
    'freq': 'H'
}


""" params = {'paramsData': paramsData, 'paramsRun': paramsRun, 'paramsBT': paramsBT, 'paramsPF': paramsPF}
json.dumps(params)
with open('params/TrixTest.json', 'w', encoding='utf-8') as f:
    json.dump(params, f, ensure_ascii=False, indent=4) """
Data, Run, BT, PF = pp.parse(paramsData, paramsRun, paramsBT, paramsPF)
runTxt, run  = Run
#logger.verifyTried(paramsTxt, Data, BT, Run)
strat = Strat()
"""
for dataTxt, data in Data: 
    
    test = ForwardTest(data)
    test.compute_entries_exits(run)
    
    for btTxt, bt in BT: 
        used_kelly = False
        for pfTxt, pf in PF:
            try :
                paramsTxt = utils.regroupParams (dataTxt, runTxt, btTxt, pfTxt)
                tried, path = logger.verifyTried(paramsTxt, data, bt, run)
                if not tried: 
                    test.compute_PF(bt, pf)
                    ptf = test.reconstruct_pf()
                    logger.log(paramsTxt, data, run, bt, pf, ptf)
                    if not used_kelly : 
                        stats = ptf.stats()
                        winrate, average_win, average_loss = stats['Win Rate [%]'] / 100, stats['Avg Winning Trade [%]'] / 100, abs(stats['Avg Losing Trade [%]'] /100) 
                        
                        pf_kelly = copy.deepcopy(pf)
                        kelly_size = test.kelly_criterion(winrate, average_win, average_loss)
                        pf_kelly['size'] = kelly_size
                        test.compute_PF(bt, pf_kelly)
                        ptf = test.reconstruct_pf()
                        utils.debug(winrate, average_win, average_loss, kelly_size)
                        utils.debug('kelly portfolio')
                        logger.log(paramsTxt, data, run, bt, pf_kelly, ptf)
                        used_kelly = True
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
"""
results_df = ranking.get_results('results')

conds = ['!End Value! > 120']
sort_expr = '-!Max Drawdown [%]!'
ranking.rank(results_df, sort_expr, conds)