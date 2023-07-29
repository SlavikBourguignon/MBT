import datetime, pytz
import collections, copy
from typing import Union 
import decorators as dct
import numpy as np


def _parseData(Data: dict) -> dict:

    def to_datetime(s : str) -> datetime.datetime:
        return datetime.datetime(*[int(elem) for elem in s.split('-')], tzinfo=pytz.timezone('UTC'))
    
    start = to_datetime(Data['download_params']['start'])
    end = to_datetime(Data['download_params']['end'])

    dp = {'start': start,
          'end': end,
          'symbols': copy.deepcopy(Data['download_params']['symbols']),
          'interval':  copy.deepcopy(Data['download_params']['interval'])}
    
    gp = copy.deepcopy(Data['get_params'])

    return {'download_params': dp, 'get_params': gp}

def _parseRun(Run: dict) -> dict:
    sn = copy.deepcopy(Run['strategy_name'])

    inputs = {}
    
    pp = 'param_product'
    for key in Run['inputs']:
        if key != pp: 
            inputs[key] = np.arange(**Run['inputs'][key])

    inputs[pp] = Run['inputs'][pp] \
                                if pp in Run['inputs'].keys() \
                                else False

    return {'strategy_name': sn, 'inputs': inputs}      


def _parseBT(BT : dict) -> dict:
    #parse backtest params
    

    def parse_timedelta(d : dict) -> datetime.timedelta:
        return datetime.timedelta(**d)
    
    length = parse_timedelta(BT['length'])
    forward = parse_timedelta(BT['forward'])

    key = 'param_product'
    params_product = BT[key] if key in BT.keys() else False
    
    return {'length': length, 
            'forward': forward,
            'param_product':params_product}

def _parsePF(PF: dict) -> dict:
    
    return copy.deepcopy(PF)


def parse(Data, Run, BT, PF):
    
    return  _parseData(Data), \
            _parseRun(Run), \
            _parseBT(BT), \
            _parsePF(PF)
