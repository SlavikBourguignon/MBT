import pandas as pd
import datetime, json, pytz
import vectorbt as vbt
import numpy as np
import matplotlib.pyplot as plt
import talib

import vbt_indicator


class ComputeIndics():
    def __init__(self, asset = 'BTCUSDT', 
                 data_interval = '1m', 
                 perf_interval = 5, 
                 start_date = datetime.datetime.now() - datetime.timedelta(days = 1), 
                 end_date = datetime.datetime.now(), 
                 to_get = 'Close', 
                 download_factory = vbt.BinanceData):
        
        self.asset = asset
        self.data_interval = data_interval
        self.perf_interval = perf_interval
        self.start_date = start_date
        self.end_date = end_date
        self.download_factory = download_factory
        self.to_get = to_get
        self.data = self.download_factory.download(
            self.asset, 
            interval = self.data_interval, 
            start = self.start_date, 
            end = self.end_date).get(self.to_get)
        self.indicators = vbt_indicator.Indicators()

    def get_perfs(self):
        self.perfs = (self.data["Close"].shift(-1-self.perf_interval)/self.data["Close"].shift(-1) - 1).fillna(0).to_numpy() * 100

    def adapt_dim(self, array):
        if np.ndim(array) == 2:
            return array
        elif np.ndim(array) == 1:
            return np.reshape(array, (-1, 1))
        else :
            raise Exception(f"Number of dimension too high: got {np.ndim(array)}, excepted 2 or less.")        

    def create_indicators(self):
        self.inputs_model = []
        for indicator, params in zip(self.indicator_list, self.params_list):
            try :
                res = indicator.run(*[self.data[input.title()] for input in indicator.input_names], **params)
                for attr in res.output_names:
                    predictors = getattr(res, attr)
                    self.inputs_model.append(self.adapt_dim(predictors.to_numpy()))
            except Exception as e:
                print(indicator)
            

        self.inputs_model = np.nan_to_num(np.concatenate(self.inputs_model, axis = 1))

    

    def normalise(self, a):
        a -= np.mean(a, axis = 0)
        a /= np.sqrt(np.var(a, axis = 0))


    def get_correls(self):
        self.correls = (self.inputs_model.T @ self.perfs) / self.perfs.shape


    def load_dict(self, dict):
        self.indicator_list = []
        self.params_list = []
        for elem in dict:
            self.indicator_list.append(getattr(self.indicators, elem["indicator"]))
            params = {}
            for key in elem["params"].keys():
                if key != "param_product":
                    params[key] = np.arange(**elem["params"][key])
                else: 
                    params[key] = elem["params"][key] == "True"
            self.params_list.append(params)
        

    
    



