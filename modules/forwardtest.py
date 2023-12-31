import vectorbt as vbt
import json
import traceback
import os, ast, collections
import pandas as pd, numpy as np
import datetime, pytz, time

import decorators as dct
from vbt_strategies import Strategy as Strat
import utils
import params_parser as parser

import warnings

warnings.filterwarnings("ignore")
     

class ForwardTest():

    

    @dct.telegram_update_backtest
    @dct.timeit
    def __init__(self, paramsData):
        self.paramsData = paramsData
        self.data = self._prepare_data(
            vbt.BinanceData.download(**paramsData['download_params']) \
                .get(**paramsData['get_params']))
        self.start_backtest = paramsData['download_params']['start']
        self.end_backtest = paramsData['download_params']['end']
        



    def _prepare_data(self, tmp_data):
        cols =  self.paramsData['get_params']['column']
        if isinstance(cols, list):
            data = {}
            for elem in cols:
                data[elem] = tmp_data[elem]
        else :
            data = {cols: tmp_data}
        return data

    

    @dct.telegram_update_backtest
    @dct.timeit
    def compute_entries_exits(self, paramsRun):
        self.paramsRun = paramsRun
        S = Strat()
        print(f"Backtesting strategy {paramsRun['strategy_name']}")
        self.strat = S.__getattribute__(paramsRun['strategy_name'])
        utils.debug(paramsRun['inputs'])
        indics = self.strat.run(**self.data, **paramsRun['inputs'])

        self.entries = indics.entries
        self.exits = indics.exits 


    #@dct.error_message_handling
    def _get_local_data(self, start, end):
        tmp_data = {}
        for key in self.data.keys():
            tmp_data[key] = self.data[key][start:end]
        return tmp_data
    

    #@dct.error_message_handling
    def _get_local_entries_exits(self, start, end):
        return self.entries[start:end], self.exits[start:end]
    

    #@dct.error_message_handling
    def _get_best_params(self,start, end):
        tmp_data = self._get_local_data(start, end)
        entries, exits = self._get_local_entries_exits (start, end)

        tmp_pf = vbt.Portfolio.from_signals(close = tmp_data['Close'], 
                                            entries = entries, 
                                            exits = exits, **self.paramsPF)
        #utils.debug(dir(tmp_pf))
        expr = self.paramsBT['optimizer']('tmp_pf')[0]
        tmp_best = eval(expr).idxmax()#tmp_pf.total_return().idxmax()
        best = {}
        for elem, value in zip(self.strat.param_names, tmp_best) :
            best[elem] = value
        return best
    

    #@dct.error_message_handling
    def _play_best_params(self,start, end, best, init_cash = 1000):
        tmp_data = self._get_local_data(start, end)
        real_res = self.strat.run(**tmp_data, **best)

        #record entries and exits
        self.entries_list.append(real_res.entries)
        self.exits_list.append(real_res.exits)

        #compute effective strat executed
        real_pf = vbt.Portfolio.from_signals(close = tmp_data['Close'], 
                                                entries = real_res.entries, 
                                                exits = real_res.exits, 
                                                **self.paramsPF, 
                                                init_cash = init_cash
                                            )
        return real_pf


    #@dct.error_message_handling
    @dct.timeit
    def compute_PF(self, paramsBT, paramsPF):
        self.paramsPF = paramsPF
        self.paramsBT = paramsBT
        self.entries_list = []
        self.exits_list = []

        #compute start and end of backtest and forward test
        start = self.start_backtest
        end = start + paramsBT['length']
        start_forward = end
        end_forward = start_forward + paramsBT['forward']

        #get best params
        tmp_best = self._get_best_params(start, end)
        
        while end_forward < self.end_backtest:
            pf = self._play_best_params(start_forward, end_forward, tmp_best)

            #print evolutions
            #print(f'Forward test between {start_forward} and '
            #      f'{end_forward} finished at {datetime.datetime.now()}')

            #compute start and end of backtest and forward test
            start = start + paramsBT['forward']
            end = end_forward
            start_forward = end
            end_forward = start_forward + paramsBT['forward']
            
            #get best params
            tmp_best = self._get_best_params(start, end)


    #@dct.error_message_handling
    @dct.timeit
    def reconstruct_pf(self):

        self.entries_list = pd.concat(self.entries_list)
        self.exits_list = pd.concat(self.exits_list)

        if self.paramsData['get_params']['column'] == 'Close':

            pf = vbt.Portfolio.from_signals(self.data.iloc[self.entries_list.index], 
                                            self.entries_list, 
                                            self.exits_list, 
                                             **self.paramsPF
                                            )
        else:
            tmp_data = self.data['Close'][self.entries_list.index]

            pf = vbt.Portfolio.from_signals(tmp_data , 
                                            self.entries_list, 
                                            self.exits_list, 
                                            **self.paramsPF
                                            )
        print(pf.stats())
        return pf
    

    #@dct.error_message_handling
    def kelly_criterion(self, winrate, average_win, average_loss):
        return winrate/average_loss - (1 - winrate) / average_win 

    #@dct.error_message_handling
    def test_time(self, Data, Run):
        end = Data['download_params']['end']
        Data['download_params']['end'] = Data['download_params']['start'] + datetime.timedelta(**{'weeks': 1})

        
        test = ForwardTest(Data)
        t0 = time.time()
        test.compute_entries_exits(Run)
        t1 = time.time()
        del test
        print(f"Testing for 1 week took {int(t1 - t0)} seconds.\n"
              f"The whole testing is estimated to take {(end - Data['download_params']['start']).days/7 * (t1 - t0)} seconds")