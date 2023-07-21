from indicator_helper import *
import pandas as pd
import numpy as np
import vectorbt as vbt


### Definition of vbt-like indicators
class Indicators():
    def __init__(self) :
        
        #No Lag Moving Average Oscillator
        self.IdcNLMAO = vbt.IndicatorFactory(
                class_name= 'NoLagMovingAverageOscillator',
                short_name = 'NLMAO',
                input_names = ["Close" ],
                param_names = ["fast_window", "slow_window"],
                output_names= ["oscilloMA"]
            ).from_apply_func(NLMAO)


        #No Lag Moving Average Derivative
        self.IdcNLMAD = vbt.IndicatorFactory(
            class_name= 'NoLagMovingAverageDerivative',
            short_name = 'NLMAD',
            input_names = ["Close" ],
            param_names = ["fast_window", "slow_window"],
            output_names= ["deriv"]
            ).from_apply_func(NLMAD)
        

        #Normalised EMA
        self.NEMA = vbt.IndicatorFactory(
            class_name = 'NormalisedEMA',
            short_name = 'NEMA',
            input_names = ["Close"],
            param_names = ["timeperiod"], 
            output_names = ["nema"]
        ).from_apply_func(NEMA)



        #Balance of Power (BOP)
        self.BOP = vbt.IndicatorFactory(
            class_name = 'BalanceOfPower',
            short_name = 'BOP',
            input_names = ["Open", "High", "Low", "Close"],
            param_names = [],
            output_names = ['bop'] 
        ).from_apply_func(BOP)

        
        #Commodity Channel Index (CCI)
        self.CCI = vbt.talib('CCI')

        
        #Ulcer Index(UI)
        self.UI = vbt.talib('ULTOSC')

        
        #Chande Momentum Oscillator(CMO)
        self.CMO = vbt.talib('CMO')


        #Hilbert Transform DC Period
        self.HTDCPERIOD = vbt.talib('HT_DCPERIOD')


        #Hilbert Transform DC Phase
        self.HTDCPHASE = vbt.talib('HT_DCPHASE')


        #Hilbert Transform PHASOR
        self.HTPHASOR = vbt.talib('HT_PHASOR')

        
        #Hilbert Transform SINE
        self.HTSINE = vbt.talib('HT_SINE')

        
        #Hilbert Transform TRENDMODE
        self.HTTRENDMODE = vbt.talib('HT_TRENDMODE')


        #Normalised KAMA
        self.NKAMA = vbt.IndicatorFactory(
            class_name = 'NormalisedKAMA',
            short_name = 'NKAMA',
            input_names = ["Close"],
            param_names = ["timeperiod"], 
            output_names = ["nkama"]
        ).from_apply_func(NKAMA)

        
        #Triple Exponential Average (TRIX)
        self.TRIX = vbt.talib('TRIX')

        
        #Normalised MACD
        self.NMACD = vbt.IndicatorFactory(
            class_name = 'NormalisedMACD',
            short_name = 'NMACD',
            input_names = ['Close'],
            param_names = ["fastperiod", "slowperiod", "signalperiod"],
            output_names = ["nmacd"]
        ).from_apply_func(NMACD)

        
        #Money Flow Index (MFI)
        self.MFI = vbt.talib('MFI')


        #Minus Directional Indicator (MDI)
        self.MDI = vbt.talib('MINUS_DI')

        
        #Minus Directional Movement (MDM)
        self.MDM = vbt.talib('MINUS_DM')


        #Plus Directional Indicator (PDI)
        self.PDI = vbt.talib('PLUS_DI')

        
        #Minus Directional Movement (MDM)
        self.PDM = vbt.talib('PLUS_DM')


        #WILLR
        self.WILLR = vbt.talib('WILLR')


        #Normalised Bollinger Bands
        self.NBBANDS = vbt.IndicatorFactory(
            class_name = 'NormalisedBollingerBands',
            short_name = 'NBBANDS',
            input_names = ['Close'],
            param_names = ['timeperiod', 'nbdevup', 'nbdevdn'],
            output_names = ['uppeband', 'middleband', 'lowerband']
        ).from_apply_func(NBBANDS)


        #Normalised Weighted Moveing Average
        self.NWMA = vbt.IndicatorFactory(
            class_name = 'NormalisedBollingerBands',
            short_name = 'NWMA',
            input_names = ['Close'],
            param_names = ['timeperiod'],
            output_names = ["nwma"]
        ).from_apply_func(NWMA)

        









        
