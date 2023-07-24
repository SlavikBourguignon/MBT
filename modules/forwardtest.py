import vectorbt as vbt
import json
import traceback
import os, ast, collections
import pandas as pd, numpy as np
import datetime, pytz

import decorators as dct
from vbt_strategies import Strategy as Strat
import utils
import params_parser as parser

class ForwardTest():
    def __init__(self, params_txt, strategy = None) -> None:
        
        self.params_txt = params_txt
        self.params = parser.parse(params_txt)

        if strategy is None :
            strat = Strat()
            self.strategy = strat.__getattribute__(self.params['strategy_name'])
        else: 
            self.strategy = strategy

        self.check_strategy()
        pb = self.params['backtest']
        
        self.params_strat = self.params['strat']
        self.start_backtest = pb['start']
        self.end_backtest = pb['end']
        self.length_backtest = pb['length']
        self.length_forward = pb['forward']
        self.run_params = self.params['strat']['run_params']
        self.entries_list = []
        self.exits_list = []
        self.data = []

    def check_strategy(self):
        if 'entries' in self.strategy.output_names and 'exits' in self.strategy.output_names and len(self.strategy.output_names) == 2:
            pass
        else :
            raise Exception("The strategy must have output_names match 'entries' and 'exits'. ")
    
    def _prepare_data(self, tmp_data):
        cols =  self.params['strat']['get_params']['column']
        if isinstance(cols, list):
            data = {}
            for elem in cols:
                data[elem] = tmp_data[elem]
        else :
            data = {cols: tmp_data}
        return data


    def _get_best_params(self,start, end):
        ps = self.params['strat']
        tmp_data = vbt.BinanceData.download(start = start, end = end ,
                                            **ps['download_params']).get(**ps['get_params'])
  
        tmp_data = self._prepare_data(tmp_data)
        
        tmp_res = self.strategy.run(**tmp_data, **self.run_params)

        tmp_pf = vbt.Portfolio.from_signals(close = tmp_data['Close'], 
                                            entries = tmp_res.entries, 
                                            exits = tmp_res.exits, **self.params['portfolio'])
            
        tmp_best = tmp_pf.total_return().idxmax()
        best = {}
        for elem, value in zip(self.strategy.param_names, tmp_best) :
            best[elem] = value
        return best
    
    def _play_best_params(self, start, end, best, init_cash = 1000):
        ps = self.params['strat']
        data = vbt.BinanceData.download(start = start, end = end ,
                                            **ps['download_params']).get(ps['get_params']['column'])
        
        self.data.append(data)

        data = self._prepare_data(data)
        real_res = self.strategy.run(**data, **best)

        #record entries and exits
        self.entries_list.append(real_res.entries)
        self.exits_list.append(real_res.exits)

        #compute effective strat executed
        real_pf = vbt.Portfolio.from_signals(close = data['Close'], 
                                             entries = real_res.entries, 
                                             exits = real_res.exits, 
                                             **self.params['portfolio'], 
                                             init_cash = init_cash
                                            )
        return real_pf

    def _backtest(self, init_cash = 1000):

        pb = self.params['backtest']

        #compute start and end of backtest and forward test
        start = self.start_backtest
        end = start + pb['length']
        start_forward = end
        end_forward = start_forward + pb['forward']

        #get best params
        tmp_best = self._get_best_params(start, end)
        cash = init_cash
        
        while end_forward < self.end_backtest:
            pf = self._play_best_params(start_forward, end_forward, tmp_best, cash)

            #record data
            cash = pf.stats()['End Value']

            #print evolutions
            print(f'Forward test between {start_forward} and {end_forward} finished at {datetime.datetime.now()}')
            print(f'Cash: {cash}')

            #compute start and end of backtest and forward test
            start = start + pb['forward']
            end = end_forward
            start_forward = end
            end_forward = start_forward + pb['forward']
            
            #get best params
            tmp_best = self._get_best_params(start, end)

        return cash
    
    def _aggregate_results(self):
        self.data = pd.concat(self.data)
        self.entries_list = pd.concat(self.entries_list)
        self.exits_list = pd.concat(self.exits_list)

        if self.params_strat['get_params']['column'] == 'Close':
            pf = vbt.Portfolio.from_signals(self.data, self.entries_list, self.exits_list, 
                                             **self.params['portfolio']
                                            )
        else:
            pf = vbt.Portfolio.from_signals(self.data['Close'], self.entries_list, self.exits_list, 
                                             **self.params['portfolio']
                                            )
        self.pf = pf

    def _getFoldersName(self): 
        pb = self.params['backtest']
        psd = self.params['strat']['download_params']
        resultsFolder = 'results'
        stratFolder = self.strategy.__name__
        symbolFolder = psd['symbols']
        itvFolder = psd['interval']
        namedir =  f'{pb["start"].date()}_' \
                    f'{pb["end"].date()}_' \
                    f'{str(pb["length"].days).split(" ")[0]}_' \
                    f'{str(pb["forward"].days).split(" ")[0]}'
        
        return resultsFolder, stratFolder, symbolFolder, itvFolder, namedir
        
    def _log(self):
        
        resultsFolder, stratFolder, symbolFolder, itvFolder, namedir = self._getFoldersName()

        utils.go_or_create(resultsFolder)
        utils.go_or_create(stratFolder)
        utils.go_or_create(symbolFolder)
        utils.go_or_create(itvFolder)
        utils.go_or_create(namedir)

        numfiles = [int(f.split('.')[0].split('_')[0]) for f in os.listdir() if os.path.isfile(f)]
        if len(numfiles) == 0:
            id = 1
        else: 
            id = max(numfiles) + 1
        self.pf.stats().to_csv(f'{id}_stats.csv')
        utils.dict_to_txt(self.params_txt, f'{id}_params')

        os.chdir('../../../../..')

    def _already_tried(self):
        try : 
            resultsFolder, stratFolder, symbolFolder, itvFolder, namedir = self._getFoldersName()

            os.chdir(f'{resultsFolder}/{stratFolder}/{symbolFolder}/{itvFolder}/{namedir}')
            return_back = '../../../../..'
        except Exception as e:
            return False, ''

        params_files = [file for file in os.listdir() if (os.path.isfile(file) and file.endswith('_params.txt'))]
        for file in params_files:
            with open(file) as f:
                d = json.load(f)

            if d == self.params_txt:
                path = os.getcwd()
                os.chdir(return_back)
                return True, path +'/' + file
            
        os.chdir(return_back)
        return False, ''
        

    def run(self, log = False):
        tried = self._already_tried()
        if tried[0]:
            print(f'The computation have already been done with these parameters.\nLook for the results in: \n{tried[1]}')
        else:
            self._backtest()
            self._aggregate_results()
            print(self.pf.stats())
            if log: 
                self._log()
        
        