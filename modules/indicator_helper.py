import pandas as pd
import numpy as np
import vectorbt as vbt


##Def of helper function for vbt indicators

#No Lag Moving Average Oscillator
def NLMAO(close, fast_window = 10, slow_window = 25):

    #Computing NoLag Short MA
    ema1 = vbt.talib('EMA').run(close, fast_window).real.to_numpy()
    ema2 = vbt.talib('EMA').run(ema1, fast_window).real.to_numpy()
    diff1 = ema1 - ema2

    ind1 = ema1 + diff1

    #Computing NoLag Long MA
    ema3 = vbt.talib('EMA').run(close, slow_window).real.to_numpy()
    ema4 = vbt.talib('EMA').run(ema3, slow_window).real.to_numpy()
    diff2 = ema3 - ema4

    ind2 = ema3 + diff2

    #Computing the oscillator
    oscilloMA = ind1 - ind2

    return oscilloMA

#No Lag Moving Average Derivative
def NLMAD(close, fast_window = 10, slow_window = 25):
    oscilloMA = NLMAO(close, fast_window, slow_window)
    deriv = np.diff(oscilloMA, axis = 0, prepend = 0)

    return deriv

#Normalised EMA
def NEMA(close, timeperiod = 20):
    nema = vbt.talib('EMA').run(close, timeperiod = timeperiod).real.to_numpy() / close
    return nema

#Balance of Power (BOP)
def BOP(Open, High, Low, Close):
    return (Close - Open)/ (High - Low)

#Normalised KAMA
def NKAMA(Close, timeperiod):
    return vbt.talib('KAMA').run(Close, 
                                 timeperiod = timeperiod).real.to_numpy() / Close

#Normalised MACD
def NMACD(Close, fastperiod, slowperiod, signalperiod):
    return vbt.talib('MACD').run(Close, 
                                 fastperiod = fastperiod, 
                                 slowperiod = slowperiod, 
                                 signalperiod = signalperiod).real.to_numpy() / Close

#Normalised Bollinger Bands
def NBBANDS(Close, timeperiod, nbdevup, nbdevdn):
    return vbt.talib('BBANDS').run(Close, 
                                   timeperiod = timeperiod, 
                                   nbdevup = nbdevup, 
                                   nbdevdn = nbdevdn).real.to_numpy() / Close

#Normalised WMA
def NWMA(Close, timeperiod):
    return vbt.talib('WMA').run(Close, 
                                timeperiod = timeperiod).real.to_numpy() / Close

#True Strategy (CryptoRobot)
def true_strat(Close, fast_ema, slow_ema):
    ema1 = vbt.talib('EMA').run(Close, fast_ema).real.to_numpy()
    ema2 = vbt.talib('EMA').run(Close, slow_ema).real.to_numpy()
    stoch_rsi = vbt.talib('STOCHRSI').run(Close).fastk.to_numpy() 
    entries = (ema1 >ema2) & (stoch_rsi <80)
    exits = (ema1 <ema2)  & (stoch_rsi > 20) 
    return entries, exits

#Triple Super Trend(CryptoRobot)
def triplestrend(High, Low, Close, ema_window = 90, stl1 =20, stm1 = 3, stl2 = 20, stm2 = 4, stl3 = 40, stm3 = 8):
    ema = vbt.talib('EMA').run(Close, ema_window).real.to_numpy()
    stoch_rsi = vbt.talib('STOCHRSI').run(Close).fastk.to_numpy() 
    st1 = vbt.pandas_ta('supertrend').run(High, Low, Close, stl1, stm1).supertd.to_numpy()
    st2 = vbt.pandas_ta('supertrend').run(High, Low, Close, stl2, stm2).supertd.to_numpy()
    st3 = vbt.pandas_ta('supertrend').run(High, Low, Close, stl3, stm3).supertd.to_numpy()
    
    entries = ((st1 + st2 + st3)>= 1) & (stoch_rsi > 80) & (ema > Close)
    exits =  ((st1 + st2 + st3) < 1) & (stoch_rsi < 20) & (ema < Close)

    return entries, exits

#Alligator(CryptoRobot)
def alligator(Close, window1, window2, window3, window4, window5, window6):
    ema1 = vbt.talib('EMA').run(Close, window1).real.to_numpy()
    ema2 = vbt.talib('EMA').run(Close, window2).real.to_numpy()
    ema3 = vbt.talib('EMA').run(Close, window3).real.to_numpy()
    ema4 = vbt.talib('EMA').run(Close, window4).real.to_numpy()
    ema5 = vbt.talib('EMA').run(Close, window5).real.to_numpy()
    ema6 = vbt.talib('EMA').run(Close, window6).real.to_numpy()
    stoch_rsi = vbt.talib('STOCHRSI').run(Close).fastk.to_numpy() 

    entries = (ema1 > ema2) & (ema2 > ema3) & (ema3 > ema4) & (ema4 > ema5) & (ema5 > ema6) & (stoch_rsi < 0.8)
    exits = (ema6 > ema1) & (stoch_rsi < 0.2) 

    return entries, exits

#Trix(CryptoRobot)
def trix(Close, ema_window, signal):
    ema1 = vbt.talib('EMA').run(Close, ema_window).real.to_numpy()
    ema2 = vbt.talib('EMA').run(ema1, ema_window).real.to_numpy()
    ema3 = vbt.talib('EMA').run(ema2, ema_window).real
    
    trix =  ema3.pct_change().to_numpy()*100
    trix_signal = vbt.talib('SMA').run(trix, signal).real.to_numpy()
    trix_histo = trix - trix_signal
    stoch_rsi  = vbt.talib('STOCHRSI').run(Close).fastk.to_numpy()

    entries = (trix_histo > 0) & (stoch_rsi < 0.8)
    exits = (trix_histo < 0) & (stoch_rsi > 0.2)

    return entries, exits

#BigWill(CryptoRobot)
def bigwill(High, Low, Close, ao1, ao2, stoch_window, willr_period):
    src = (High+ Low) 
    ao = vbt.talib('SMA').run(src, ao1).real.to_numpy() - vbt.talib('SMA').run(src, ao2).real.to_numpy()
    stoch_rsi = vbt.talib('STOCHRSI').run(Close, stoch_window).fastk.to_numpy()
    willr = vbt.talib('WILLR').run(High, Low, Close, willr_period).real.to_numpy()

    entries = (ao > 0) & (willr < -85)
    exits = ((ao < 0) & (stoch_rsi > 0.2)) | (willr > -10)

    return entries, exits

#VuManChu(CryptoRobot)
def vumanchustrat(Open,High, Low, Close, period, mfimult, fastema, slowema):
    hcl3 = (High + Low + Close)/3
    esa = vbt.talib('EMA').run(hcl3, period).real.to_numpy()
    de = vbt.talib('EMA').run(np.abs(hcl3 - esa), period).real.to_numpy()
    ci = (hcl3 - esa) / (0.015*de)
    wave1 = vbt.talib('EMA').run(ci, period)
    wave2 = vbt.talib('SMA').run(wave1.real.to_numpy(), period).real.to_numpy()

    cross = wave1.close_crossed_above(wave2).to_numpy()

    wave1 = wave1.real.to_numpy()

    mfi  = (Open - Close) / (High - Low) * mfimult

    ema1 = vbt.talib('EMA').run(Close, fastema).real.to_numpy()
    ema2 = vbt.talib('EMA').run(Close, slowema).real.to_numpy()

    lowl = pd.Series(Low.flatten()).rolling(fastema).min().shift(1).to_numpy()
    highh = pd.Series(High.flatten()).rolling(fastema).max(fastema).shift(1).to_numpy()
    entries = (ema1 >= ema2) & (Close > ema1) & (mfi > 0) & (wave1 < 0 ) & (wave2 < wave1) & cross 
    exits = (Close.flatten() < lowl) | (Close.flatten() > highh)

    return entries, exits

#BollingerTrend(CryptoRobot)
def boltrend(Close, window, std, minspread, emawindow):
    bbands = vbt.talib('BBANDS').run(Close, window, std, std)
    rel_spread = (pd.Series(bbands.upperband.to_numpy().flatten() / bbands.lowerband.to_numpy().flatten()).shift(1).fillna(0).to_numpy() - 1) * 100
    ema = vbt.talib('EMA').run(Close, emawindow).real.to_numpy()

    entries = bbands.upperband_crossed_below(Close).to_numpy().flatten() & (rel_spread > minspread).flatten() & (Close > ema).flatten()
    exits = Close < bbands.middleband

    return entries, exits

#SuperReversal(CryptoRobot)
def superreversal(High, Low, Close, fastema, slowema, stl1, stm1):
    ema1 = vbt.talib('EMA').run(Close, fastema).real.to_numpy()
    ema2 = vbt.talib('EMA').run(Close, slowema).real.to_numpy()
    st1 = vbt.pandas_ta('supertrend').run(High, Low, Close, stl1, stm1).supertd.to_numpy()

    entries = (ema1 > ema2) & (st1 > 0) & (Low < ema1)
    exits = (st1 < 0) & (High > ema1)

    return entries,  exits

