import sys 
sys.path.append('modules/')
from forwardtest import ForwardTest
from vbt_strategies import Strategy as Strat
import  metaparams as mp
import utils
import warnings

warnings.filterwarnings("ignore")

params = {
    'strategy_name': 'Trix',
    'backtest': {
        'start': '2017-10-1',
        'end': '2023-1-1',
        'length': [{
            'weeks': 4  #durée pendant laquelle on optimise les paramètres
        }, {
            'weeks': 6  #durée pendant laquelle on optimise les paramètres
        }],
        'forward': [{
            'weeks': 2  #durée pendant laquelle on joue les paramètres optimisés
        },{
            'weeks': 1  #durée pendant laquelle on joue les paramètres optimisés
        }], 
        'params_product': True
        
    },
    'strat':{
        'download_params': {
            'symbols': 'BTCUSDT',
            'interval': '1h',            
        },
        'get_params': {
            'column': ['Close']
        },
        'run_params': { 
            'ema_window': {'start': 5, 'stop': 20, 'step': 1},
            'signal': {'start': 10, 'stop': 30, 'step': 1},
            'param_product': True
        }, 
    },
    'portfolio': {'freq': 'H' ,
                  'fees' : 0.1/100,
                  'size_type': 'Percent',
                  'size': .3} #proportion du portefeuille à investir dans chaque trade
}

strat = Strat()
paramsList = mp.split(params)
for i, p in enumerate(paramsList):
    try:
        test = ForwardTest(p)
        test.run(log = True)
        print(f'Finished computing the set of parameters number {i}')
    except Exception as e:
        print('Failed in test.py with: \n', e)
