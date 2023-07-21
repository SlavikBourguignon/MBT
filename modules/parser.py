import datetime, pytz
import collections
from typing import Union 
import decorators as dct

def parse(params : dict):
    #parse backtest params
    backtest = params['backtest']

    def to_datetime(s : str) -> datetime.datetime:
        return datetime.datetime(*[int(elem) for elem in s.split('-')], tzinfo=pytz.timezone('UTC'))
    
    start = to_datetime(backtest['start'])
    end = to_datetime(backtest['end'])

    @dct.map
    def parse_timedelta(d : dict) -> datetime.timedelta:
        return datetime.timedelta(**d)
    
    length = parse_timedelta(backtest['length'])
    forward = parse_timedelta(backtest['timedelta'])

    