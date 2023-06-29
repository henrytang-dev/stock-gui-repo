import yfinance as yf
import time
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import mplfinance as mpf
from mplfinance import _panels as ps
import matplotlib as mpl
from itertools import count
import matplotlib.animation as animation
mpl.rcParams.update({'font.size': 9})


def pullData (stock):
    data = yf.download(tickers = stock, period = '1d', interval = '5m')
    data.to_csv(stock + '.txt')


def calculateRSI(stock):
    data = yf.download(tickers = stock, period = '1d', interval = '5m')

    # specifying strategy parameters
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    fee = 0.0005

    # coding technical analysis signals (this employs the math involved with calculating the RSI)
    data['returns'] = data['Close'].pct_change()
    data['Up'] = np.maximum(data['Close'].diff(), 0)
    data['Down'] = np.maximum(-data['Close'].diff(), 0)
    data['RS'] = data['Up'].rolling(rsi_period).mean()/data['Down'].rolling(rsi_period).mean()
    rsi = 100 - 100/(1 + data['RS'])
    return rsi

# calculate MACD values
def ExpMovingAverage(stock, window):
    # calculating exponential moving average; ewm(): exponentially weighted calculation, mean(): average
    data = yf.download(tickers=stock, period='1d', interval='5m')
    return data['Close'].ewm(span=window, adjust=False).mean()

def computeMACD(stock):
    # MACD line defined as difference between 12 and 26-day moving averages
    return ExpMovingAverage(stock, 12) - ExpMovingAverage(stock, 26)

def computeSignal(stock):
     # MACD signal defined as 9 period exponential moving average of MACD line
    return computeMACD(stock).ewm(span=9, adjust=False).mean()

def createHistogram(stock):
     # calculate difference between MACD Line and MACD signal to plot as histogram
    return computeMACD(stock) - computeSignal(stock)


# calculating ADX
def computeATR(stock, window):
    data = yf.download(tickers=stock, period='1d', interval='5m')

    tr1 = pd.DataFrame(data['High'] - data['Low'])
    tr2 = pd.DataFrame(abs(data['High'] - data['Close'].shift()))
    tr3 = pd.DataFrame(abs(data['Low'] - data['Close'].shift()))
    tr = pd.concat([tr1, tr2, tr3], axis = 1).max(axis = 1)
    return tr.rolling(window).mean()

def computePosDI(stock):
    data = yf.download(tickers=stock, period='1d', interval='5m')

    # +DM, -DM
    plus_dm = data['High'].diff()
    minus_dm = data['Low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    plus_di = 100 * (plus_dm.ewm(alpha = 1/14).mean() / computeATR(stock, 14))

    return plus_di

def computeNegDI(stock):
    data = yf.download(tickers=stock, period='1d', interval='5m')

    # +DM, -DM
    plus_dm = data['High'].diff()
    minus_dm = data['Low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    minus_di = abs(100 * (minus_dm.ewm(alpha = 1/14).mean() / computeATR(stock, 14)))

    # -DI
    return minus_di

def computeADX (stock):
    directional_index = np.abs((computePosDI(stock) - computeNegDI(stock))/(computePosDI(stock) + computeNegDI(stock)))
    return 100 * (directional_index.ewm(span=14, adjust=False).mean())

    
def graphData(stock):
    # downloading stock data
    data = yf.download(tickers = stock, period = '1d', interval = '5m')
    data = data.drop(columns='Adj Close')

    # styling
    mc = mpf.make_marketcolors(up='#9eff15', down='#ff1717', wick='w', volume='#00ffe8')
    s = mpf.make_mpf_style(base_mpf_style='nightclouds',
                           marketcolors=mc,
                           figcolor='#07000d',
                           edgecolor='#5998ff')
    
    # setting horizontal lines
    data['rsi_lower'] = 30
    data['rsi_upper'] = 70
    data['adx_line'] = 25

    # making addplots for technical analysis
    ap0 = [mpf.make_addplot(data['Volume'],ylim=(0, 5*data['Volume'].max()), panel=1, color='#00ffe8', fill_between=dict(y1=data['Volume'].values, color='#00ffe8')),
           # RSI related plots
           mpf.make_addplot(calculateRSI(stock), panel=0, ylim=(0,100), color='#00ffe8', width=0.5),
           mpf.make_addplot(data['rsi_lower'], panel=0, color='#386d13', width=0.6),
           mpf.make_addplot(data['rsi_upper'], panel=0, color='#8f2020', width=0.6),
           
           # MACD related plots
           mpf.make_addplot(ExpMovingAverage(stock, 12), width=0.7, panel=1),
           mpf.make_addplot(ExpMovingAverage(stock, 26), width=0.7, panel=1),
           mpf.make_addplot(createHistogram(stock), type='bar', width=0.5, panel=2, alpha=1, secondary_y=False),
           mpf.make_addplot(computeMACD(stock), panel=2, secondary_y=True, width=0.7),
           mpf.make_addplot(computeSignal(stock), panel=2, secondary_y=True, width=0.7),

           # ADX related plots
           mpf.make_addplot(computeNegDI(stock), panel=3, ylim=(0, 100), width=0.7),
           mpf.make_addplot(computePosDI(stock), panel=3, ylim=(0, 100), width=0.7),
           mpf.make_addplot(computeADX(stock), panel=3, ylim=(0, 100), width=0.7),
           mpf.make_addplot(data['adx_line'], panel=3, width=0.7)
           ]

    # plotting and graphing
    fig, axlist = mpf.plot(data,
                   style=s,
                   type='candle',
                   title=stock +' Stock Data',
                   ylabel='Price Level',
                   returnfig=True,
                   ylabel_lower='RSI',
                   xlabel='DATE',
                   addplot=ap0,
                   main_panel=1,
                   num_panels=4)
    
    # editing labels & ticks
    axlist[0].set_yticklabels([])
    axlist[0].set_ylabel('RSI')
    axlist[3].set_yticklabels([])
    axlist[4].set_yticklabels([])
    axlist[4].set_ylabel('MACD')
    axlist[5].set_yticklabels([])
    axlist[6].set_yticklabels([])
    axlist[6].set_ylabel('ADX')

    mpf.show()