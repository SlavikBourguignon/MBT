from indicator_helper import *
import pandas as pd
import numpy as np
import vectorbt as vbt

class Strategy:
    def __init__(self) :
        #True Strategy indicator
        self.TrueStrat = vbt.IndicatorFactory(
            class_name= 'TrueStrat',
            short_name = 'TS',
            input_names = ["Close"] ,
            param_names = ["fast_ema", "slow_ema"],
            output_names= ["entries", "exits"]
        ).from_apply_func(true_strat)
        
        #Triple Super Trend indicator
        self.TripleSTrend = vbt.IndicatorFactory(
            class_name= 'TripleSTrend',
            short_name = '3ST',
            input_names = ["High", "Low", "Close"] ,
            param_names = ["ema_window", "stl1", "stm1", "stl2", "stm2", "stl3", "stm3"],
            output_names= ["entries", "exits"]
        ).from_apply_func(triplestrend)

        #Alligator
        self.Alligator = vbt.IndicatorFactory(
            class_name= 'Alligator',
            short_name = 'ALGT',
            input_names = ["Close"] ,
            param_names = ["window1", "window2", "window3", "window4", "window5", "window6",],
            output_names= ["entries", "exits"]
        ).from_apply_func(alligator)

        #Trix
        self.Trix = vbt.IndicatorFactory(
            class_name= 'Trix',
            short_name = 'TRX',
            input_names = ["Close"] ,
            param_names = ["ema_window", "signal"],
            output_names= ["entries", "exits"]
            ).from_apply_func(trix)
        
        #BigWill
        self.BigWill = vbt.IndicatorFactory(
            class_name= 'BigWill',
            short_name = 'BW',
            input_names = ["High", "Low", "Close"] ,
            param_names = ["ao1", "ao2", "stoch_window", "willr_period"],
            output_names= ["entries", "exits"]
            ).from_apply_func(bigwill)

        #VuManChuStrat
        self.VMCstrat = vbt.IndicatorFactory(
            class_name= 'VuManChu',
            short_name = 'VMC',
            input_names = ["Open", "High", "Low", "Close"] ,
            param_names = ["period", "mfimult", "fastema", "slowema"],
            output_names= ["entries", "exits"]
            ).from_apply_func(vumanchustrat)

        #Bollinger Trend
        self.BolTrend = vbt.IndicatorFactory(
            class_name= 'BolTrend',
            short_name = 'BT',
            input_names = ["Close"] ,
            param_names = ["window", "std", "minspread", "emawindow"],
            output_names= ["entries", "exits"]
            ).from_apply_func(boltrend)
            
        #SuperReversal
        self.SuperReversal = vbt.IndicatorFactory(
            class_name= 'SuperRevesal',
            short_name = 'SR',
            input_names = ["High", "Low", "Close"] ,
            param_names = ["fastema", "slowema", "stl1", "stm1"],
            output_names= ["entries", "exits"]
            ).from_apply_func(superreversal)