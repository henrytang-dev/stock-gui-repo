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
import utils

stock = input('Please enter a ticker symbol: ')
data = yf.download(tickers = stock, period = '1d', interval = '5m')


# setting horizontal lines
data['rsi_lower'] = 30
data['rsi_upper'] = 70
data['adx_line'] = 25

ap0 = [
        mpf.make_addplot(data['Volume'], type='bar', ylim=(0, 5*data['Volume'].max()), panel=1, color='#00ffe8'),
           # RSI related plots
           mpf.make_addplot(utils.calculateRSI(stock), panel=0, ylim=(0,100), color='#00ffe8', width=0.5),
           mpf.make_addplot(data['rsi_lower'], panel=0, color='#386d13', width=0.6),
           mpf.make_addplot(data['rsi_upper'], panel=0, color='#8f2020', width=0.6),
           
           # MACD related plots
           mpf.make_addplot(utils.ExpMovingAverage(stock, 12), width=0.7, panel=1),
           mpf.make_addplot(utils.ExpMovingAverage(stock, 26), width=0.7, panel=1),
           mpf.make_addplot(utils.createHistogram(stock), type='bar', width=0.5, panel=2, alpha=1, secondary_y=False),
           mpf.make_addplot(utils.computeMACD(stock), panel=2, secondary_y=True, width=0.7),
           mpf.make_addplot(utils.computeSignal(stock), panel=2, secondary_y=True, width=0.7),

           # ADX related plots
           mpf.make_addplot(utils.computeNegDI(stock), panel=3, ylim=(0, 100), width=0.7),
           mpf.make_addplot(utils.computePosDI(stock), panel=3, ylim=(0, 100), width=0.7),
           mpf.make_addplot(utils.computeADX(stock), panel=3, ylim=(0, 100), width=0.7),
           mpf.make_addplot(data['adx_line'], panel=3, width=0.7)
           ]


# styling
mc = mpf.make_marketcolors(up='#9eff15', down='#ff1717', wick='w', volume='#00ffe8')
s = mpf.make_mpf_style(base_mpf_style='nightclouds',
                        marketcolors=mc,
                        figcolor='#07000d',
                        edgecolor='#5998ff')


fig, axlist = mpf.plot(data,
                style=s,
                type='candle',
                title=stock + ' Stock Data',
                returnfig=True,
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

ax_main = axlist[2]
ax_volu = axlist[3]
ax_emav = ax_main
ax_hist = axlist[4]
ax_macd = axlist[5]
ax_sign = ax_macd

ax_rl = axlist[1]
ax_ru = ax_rl
ax_rsi = axlist[0]

ax_negDI = axlist[6]
ax_posDI = ax_negDI
ax_ADX = axlist[6]
ax_thresh = ax_negDI


def animate(ival):
    if (20+ival) > len(data):
        print('no more data to plot')
        ani.event_source.interval *= 3
        if ani.event_source.interval > 12000:
            exit()
        return
    df = data.iloc[0:(30+ival)]

    # variables
    # MACD
    exp12 = df['Close'].ewm(span=12, adjust=False).mean()
    exp26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal

    # RSI
    df['returns'] = df['Close'].pct_change()
    df['Up'] = np.maximum(df['Close'].diff(), 0)
    df['Down'] = np.maximum(-df['Close'].diff(), 0)
    df['RS'] = df['Up'].rolling(14).mean()/df['Down'].rolling(14).mean()
    rsi = 100 - 100/(1 + df['RS'])

    # ADX
    tr1 = pd.DataFrame(df['High'] - df['Low'])
    tr2 = pd.DataFrame(abs(df['High'] - df['Close'].shift()))
    tr3 = pd.DataFrame(abs(df['Low'] - df['Close'].shift()))
    tr = pd.concat([tr1, tr2, tr3], axis = 1).max(axis = 1)
    atr = tr.rolling(14).mean()

    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    negDI = abs(100 * (minus_dm.ewm(alpha = 1/14).mean() / atr))
    posDI = 100 * (plus_dm.ewm(alpha = 1/14).mean() / atr)

    directional_index = np.abs((posDI - negDI)/(posDI + negDI))
    adx = 100 * (directional_index.ewm(span=14, adjust=False).mean())

    df['rsi_lower'] = 30
    df['rsi_upper'] = 70
    df['adx_line'] = 25

    ap0 = [
        mpf.make_addplot(df['Volume'], type='bar', ylim=(0, 5*data['Volume'].max()), panel=1, color='#00ffe8', ax=ax_volu),
           # MACD related plots
           mpf.make_addplot(exp12, width=0.7, panel=1, ax=ax_emav),
           mpf.make_addplot(exp26, width=0.7, panel=1, ax=ax_emav),
           mpf.make_addplot(histogram, type='bar', width=0.5, panel=2, alpha=1, ax=ax_hist),
           mpf.make_addplot(macd, panel=2, width=0.7, ax=ax_macd),
           mpf.make_addplot(signal, panel=2,  width=0.7, ax=ax_sign),
           
           # RSI related plots
           mpf.make_addplot(rsi, panel=0, ylim=(0,100), color='#00ffe8', width=0.5, ax=ax_rsi),
           mpf.make_addplot(df['rsi_lower'], panel=0, color='#386d13', width=0.6, ax=ax_rl),
           mpf.make_addplot(df['rsi_upper'], panel=0, color='#8f2020', width=0.6, ax=ax_ru),


           # ADX related plots
           mpf.make_addplot(negDI, panel=3, ylim=(0, 100), width=0.7, ax=ax_negDI),
           mpf.make_addplot(posDI, panel=3, ylim=(0, 100), width=0.7, ax=ax_posDI),
           mpf.make_addplot(adx, panel=3, ylim=(0, 100), width=0.7, ax=ax_ADX),
           mpf.make_addplot(df['adx_line'], panel=3, width=0.7, ax=ax_thresh)
           ]
    
    for ax in axlist:
        ax.clear()

    # editing labels & ticks
    axlist[0].set_yticklabels([])
    axlist[0].set_ylabel('RSI')
    axlist[3].set_yticklabels([])
    axlist[4].set_yticklabels([])
    axlist[4].set_ylabel('MACD')
    axlist[5].set_yticklabels([])
    axlist[6].set_yticklabels([])
    axlist[6].set_ylabel('ADX')

    mpf.plot(df,
            style=s,
            type='candle',
            xlabel='DATE',
            addplot=ap0,
            main_panel=1,
            num_panels=4,
            ax=ax_main)



ani = animation.FuncAnimation(fig,animate,interval=500)
mpf.show()