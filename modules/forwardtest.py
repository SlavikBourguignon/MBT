import vectorbt as vbt
import json
import pandas as pd
import numpy as np
import datetime, pytz
import decorators as dct
import traceback
from vbt_strategies import Strategy as Strat
import utils
import os, ast

class ForwardTest():
    def __init__(self, params, strategy = None) -> None:
        if strategy is None :
            strat = Strat()
            self.strategy = strat.__getattribute__(params['strategy_name'])
        else: 
            self.strategy = strategy
        self.check_strategy()
        params_backtest = params['backtest']
        self.params = params
        self.params_strat = params['strat']
        self.start_backtest = datetime.datetime(*[int(elem) for elem in params_backtest['start'].split('-')], tzinfo=pytz.timezone('UTC'))
        self.end_backtest = datetime.datetime(*[int(elem) for elem in params_backtest['end'].split('-')], tzinfo=pytz.timezone('UTC'))
        self.length_backtest = datetime.timedelta(**params_backtest['length'])
        self.length_forward = datetime.timedelta(**params_backtest['forward'])
        self.entries_list = []
        self.exits_list = []
        self.data = []

    def check_strategy(self):
        if 'entries' in self.strategy.output_names and 'exits' in self.strategy.output_names and len(self.strategy.output_names) == 2:
            pass
        else :
            raise Exception("The strategy must have output_names match 'entries' and 'exits'. ")
        
    def _get_run_params(self):
        run_params = {}
        for key in self.params_strat['run_params']:
            if key != "param_product":
                run_params[key] = np.arange(**self.params_strat["run_params"][key])
            else: 
                run_params[key] = self.params_strat["run_params"][key] == "True"
        return run_params
    
    def _prepare_data(self, tmp_data):
        if type(self.params_strat['get_params']['column']) == list:
            data = {}
            for elem in self.params_strat['get_params']['column']:
                data[elem] = tmp_data[elem]
        else :
            data = {self.params_strat['get_params']['column']: tmp_data}
        return data


    def _get_best_params(self,start, end):
        tmp_data = vbt.BinanceData.download(start = start, end = end ,
                                            symbols= self.params_strat['download_params']['symbols'],
                                            interval = self.params_strat['download_params']['interval']).get(**self.params_strat['get_params'])
        run_params = self._get_run_params()
        tmp_data = self._prepare_data(tmp_data)
        
        tmp_res = self.strategy.run(**tmp_data, **run_params)
        tmp_pf = vbt.Portfolio.from_signals(close = tmp_data['Close'], 
                                            entries = tmp_res.entries, 
                                            exits = tmp_res.exits, **self.params['portfolio'])
            
        tmp_best = tmp_pf.total_return().idxmax()
        best = {}
        for elem, value in zip(self.strategy.param_names, tmp_best) :
            best[elem] = value
        return best
    
    def _play_best_params(self, start, end, best, init_cash = 1000):
        data = vbt.BinanceData.download(start = start, end = end ,
                                            **self.params_strat['download_params']).get(self.params_strat['get_params']['column'])
        self.data.append(data)

        data = self._prepare_data(data)
        real_res = self.strategy.run(**data, **best)

        self.entries_list.append(real_res.entries)
        self.exits_list.append(real_res.exits)

        real_pf = vbt.Portfolio.from_signals(close = data['Close'], 
                                             entries = real_res.entries, 
                                             exits = real_res.exits, 
                                             **self.params['portfolio'], 
                                             init_cash = init_cash
                                            )
        return real_pf

    def _backtest(self, init_cash = 1000):

        #compute start and end of backtest and forward test
        start = self.start_backtest
        end = start + datetime.timedelta(**self.params['backtest']['length'])
        start_forward = end
        end_forward = start_forward + datetime.timedelta(**self.params['backtest']['forward'])

        #get best params
        tmp_best = self._get_best_params(start, end)
        cash = init_cash

        #record entries and exits
        
        while end_forward < self.end_backtest:
            pf = self._play_best_params(start_forward, end_forward, tmp_best, cash)

            #record data
            cash = pf.stats()['End Value']

            #print evolutions
            print(f'Forward test between {start_forward} and {end_forward} finished at {datetime.datetime.now()}')
            print(f'Cash: {cash}')

            #compute start and end of backtest and forward test
            start = end_forward - datetime.timedelta(**self.params['backtest']['length'])
            end = end_forward
            start_forward = end
            end_forward = start_forward + datetime.timedelta(**self.params['backtest']['forward'])

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
    
    def _log(self):
        #stack = traceback.extract_stack()
        #splitterIndex = stack[-1].filename.rfind('/')
        #parentFolder = stack[-1].filename[:splitterIndex]
        resultsFolder = 'results'
        stratFolder = self.strategy.__name__
        symbolFolder = self.params['strat']['download_params']['symbols']
        itvFolder = self.params['strat']['download_params']['interval']
        namedir =  f'{self.params["backtest"]["start"]}_' \
                    f'{self.params["backtest"]["start"]}_' \
                    f'{str(datetime.timedelta(**self.params["backtest"]["length"])).split(" ")[0]}_' \
                    f'{str(datetime.timedelta(**self.params["backtest"]["forward"])).split(" ")[0]}'

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
        utils.dict_to_txt(self.params, f'{id}_params')

    def _already_tried(self):
        try : 
            resultsFolder = 'results'
            stratFolder = self.strategy.__name__
            symbolFolder = self.params['strat']['download_params']['symbols']
            itvFolder = self.params['strat']['download_params']['interval']
            namedir =  f'{self.params["backtest"]["start"]}_' \
                        f'{self.params["backtest"]["start"]}_' \
                        f'{str(datetime.timedelta(**self.params["backtest"]["length"])).split(" ")[0]}_' \
                        f'{str(datetime.timedelta(**self.params["backtest"]["forward"])).split(" ")[0]}'

            os.chdir(f'{resultsFolder}/{stratFolder}/{symbolFolder}/{itvFolder}/{namedir}')
            return_back = '../../../../..'
        except:
            return False, ''

        params_files = [file for file in os.listdir() if (os.path.isfile(file) and file.endswith('_params.txt'))]
        for file in params_files:
            with open(file) as f:
                d = ast.literal_eval(f.read())['dict']
            if d == self.params:
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
        
        