import sys
sys.path.append('modules')

import decorators as dct
import datetime
import itertools
from metaparams import duplicate_length_forward

params = {
    'strategy_name': 'Trix',
    'backtest': {
        'start': '2017-10-1',
        'end': '2017-12-1',
        'length': [{
            'weeks': 4  #durée pendant laquelle on optimise les paramètres
        }, {
            'weeks': 3  #durée pendant laquelle on optimise les paramètres
        }],
        'forward': [{
            'weeks': 2  #durée pendant laquelle on joue les paramètres optimisés
        },{
            'weeks': 5  #durée pendant laquelle on joue les paramètres optimisés
        }], 
        'params_product': False
        
    }
}

paramslist = duplicate_length_forward(params)

print(paramslist)