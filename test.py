import sys 
sys.path.append('modules/')
from forwardtest import ForwardTest
from vbt_strategies import Strategy as Strat
import warnings
warnings.filterwarnings("ignore")

params = {
    'backtest': {
        'start': '2017-10-1',
        'end': '2017-12-1',
        'length': {
            'weeks': 4  #durée pendant laquelle on optimise les paramètres
        },
        'forward': {
            'weeks': 2  #durée pendant laquelle on joue les paramètres optimisés
        },
        
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
            'param_product': 'True'
        }, 
    },
    'portfolio': {'freq': 'H' ,
                  'fees' : 0.1/100,
                  'size_type': 'Percent',
                  'size': .1} #proportion du portefeuille à investir dans chaque trade
}

strat = Strat()
test = ForwardTest(params, strat.Trix)
test.run()