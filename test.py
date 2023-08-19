import sys 
sys.path.append('modules/')
import warnings

warnings.filterwarnings("ignore")


from forwardtest import ForwardTest
from vbt_strategies import Strategy as Strat
import  metaparams as mp
import params_parser as pp
import utils, logger





paramsData = {
        'download_params': {
            'start': '2017-10-1',
            'end': '2019-1-1',
            'symbols': ['BTCUSDT', 'ETHUSDT' ],
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
    'length': [{
        'weeks': 4  #durée pendant laquelle on optimise les paramètres
    },{
        'weeks': 6  #durée pendant laquelle on optimise les paramètres
    }],
    'forward': {
        'weeks': 2  #durée pendant laquelle on joue les paramètres optimisés
    }, 
    #'param_product': True   
}

paramsPF = {
    'fees' : 0.1/100,
    'size_type': 'Percent',
    'size': [0.3, 1], 
    'freq': 'H'
}

Data, Run, BT, PF = pp.parse(paramsData, paramsRun, paramsBT, paramsPF)
runTxt, run  = Run
#logger.verifyTried(paramsTxt, Data, BT, Run)
strat = Strat()
for dataTxt, data in Data: 
    
    test = ForwardTest(data)
    test.compute_entries_exits(run)
    for btTxt, bt in BT: 
        for pfTxt, pf in PF:
            try :
                paramsTxt = utils.regroupParams (dataTxt, runTxt, btTxt, pfTxt)
                tried, path = logger.verifyTried(paramsTxt, data, bt, run)
                if not tried: 
                    test.compute_PF(bt, pf)
                    ptf = test.reconstruct_pf()
                    logger.log(paramsTxt, data, run, bt, pf, ptf)

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