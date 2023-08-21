import datetime, pytz
import collections, copy
from typing import Union 
import decorators as dct
import numpy as np
import utils
from lark import Lark, Transformer, v_args


def _to_datetime(s : str) -> datetime.datetime:
        return datetime.datetime(*[int(elem) for elem in s.split('-')], tzinfo=pytz.timezone('UTC'))

@dct.map_args
def _to_timedelta(d : dict) -> datetime.timedelta:
        return datetime.timedelta(**d)
   
@dct.product_args
def _duplicate_elem(path : tuple, value : any, d: dict) -> dict:
    cp = copy.deepcopy(d)
    if len(path) > 1 and isinstance(path, tuple):
        s = cp[path[0]]
        for key in path[1:-1] :
            s = s[key]
        s[path[-1]] = value

    
    else:
        cp.pop(path[0])
        cp[path[0]] = value
    return cp

def _extend_first_level_dict(d : dict):
    dL = copy.deepcopy(d)
    i = 0
    for key in dL.keys():
        dL = _duplicate_elem((key,), d[key], dL) 
        i+= 1
    return dL

def _extendData(Data: dict)-> list[dict]:
    
    dp = copy.deepcopy(Data['download_params'])
    dp = _extend_first_level_dict(dp)
    gp = copy.deepcopy(Data['get_params'])

    return _extend_first_level_dict({'download_params': dp, 'get_params': gp})

@dct.map_args
def _parseData(dataTxt: dict) -> [dict, dict]:
    dp = copy.deepcopy(dataTxt['download_params'])
    start = _to_datetime(dataTxt['download_params']['start'])
    end = _to_datetime(dataTxt['download_params']['end'])

    dp.pop('start')
    dp['start'] = start 
    dp.pop('end')
    dp['end'] = end
    
    gp = copy.deepcopy(dataTxt['get_params'])

    return dataTxt, {'download_params': dp, 'get_params': gp}

@dct.map_args
def _parseRun(runTxt: dict) -> [dict, dict]:
    sn = copy.deepcopy(runTxt['strategy_name'])

    inputs = {}
    
    pp = 'param_product'
    for key in runTxt['inputs']:
        if key != pp: 
            inputs[key] = np.arange(**runTxt['inputs'][key])

    inputs[pp] = runTxt['inputs'][pp] \
                                if pp in runTxt['inputs'].keys() \
                                else False

    return runTxt, {'strategy_name': sn, 'inputs': inputs}      

def _extendBT(BT: dict)-> list[dict]:
    return _extend_first_level_dict(BT)

@dct.map_args
def _parseBT(btTxt : dict) -> [dict, dict]:
    #parse backtest params
    
    length = _to_timedelta(btTxt['length'])
    forward = _to_timedelta(btTxt['forward'])
    optimizertxt = btTxt['optimizer'] if 'optimizer' in btTxt.keys() else '"total_return"'

    def wrapper(s, optimizertxt):
        i = 0
        nbquotes = 0 
        prev_add = f'{s}.'
        post_add = '()'
        while True:
            if i >= len(optimizertxt):
                break
            if optimizertxt[i] == '"':
                if nbquotes%2 == 0:
                    optimizertxt = optimizertxt[:i] + prev_add + optimizertxt[i+1:]
                    i += len(prev_add)
                if nbquotes%2 == 1:
                    optimizertxt = optimizertxt[:i] + post_add + optimizertxt[i+1:]
                    i+= len(post_add)
                nbquotes+=1
            i+=1
        return optimizertxt

    optimizer = lambda s: wrapper(s, optimizertxt)


    return btTxt, {'length': length, 
            'forward': forward,
            'optimizer': optimizer
        }

def _extendPF(PF: dict)-> list[dict]:
    return _extend_first_level_dict(copy.deepcopy(PF))

@dct.map_args
def _parsePF(pfTxt: dict) -> [dict, dict]:
    
    return pfTxt, pfTxt


def parse(Data, Run, BT, PF):
    
    return  _parseData(_extendData(Data)), \
            _parseRun(Run), \
            _parseBT(_extendBT(BT)), \
            _parsePF(_extendPF(PF))