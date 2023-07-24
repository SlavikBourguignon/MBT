import datetime, pytz
import collections, copy
from typing import Union 
import decorators as dct
import numpy as np

def _parse_backtest(backtest : dict) -> dict:
    #parse backtest params
    def to_datetime(s : str) -> datetime.datetime:
        return datetime.datetime(*[int(elem) for elem in s.split('-')], tzinfo=pytz.timezone('UTC'))
    
    start = to_datetime(backtest['start'])
    end = to_datetime(backtest['end'])

    def parse_timedelta(d : dict) -> datetime.timedelta:
        return datetime.timedelta(**d)
    
    length = parse_timedelta(backtest['length'])
    forward = parse_timedelta(backtest['forward'])

    key = 'params_product'
    params_product = backtest[key] if key in backtest.keys() else False
    return {'start': start, 
                'end': end,
                'length': length, 
                'forward': forward,
                'params_product':params_product}

def _parse_strat(strat: dict) -> dict:
    #for now I only need to parse strat['run_params] 
    run_params = {}
    for key in strat['run_params']:
        if key != "param_product":
            run_params[key] = np.arange(**strat["run_params"][key])
        else: 
            run_params[key] = strat["run_params"][key] 

    strat['run_params'] = run_params
    return strat


def parse(params):
    copy_params = copy.deepcopy(params)
    copy_params['backtest'] = _parse_backtest(copy_params['backtest'])
    copy_params['strat'] = _parse_strat(copy_params['strat'])
    
    return copy_params