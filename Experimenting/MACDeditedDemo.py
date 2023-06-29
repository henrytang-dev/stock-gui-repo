import pandas as pd
import mplfinance as mpf
import matplotlib.animation as animation
import yfinance as yf
import numpy as np
import utils

mpf.__version__
stock='AAPL'
df = yf.download(tickers='AAPL', period='2d', interval='5m')
df.drop(columns='Adj Close')
df.to_csv('AAPL.csv')
df = pd.read_csv('AAPL.csv', index_col=0, parse_dates=True, delimiter=',')

# =======
#  MACD:

exp12     = df['Close'].ewm(span=12, adjust=False).mean()
exp26     = df['Close'].ewm(span=26, adjust=False).mean()
macd      = exp12 - exp26
signal    = macd.ewm(span=9, adjust=False).mean()
histogram = macd - signal

apds = [
           # RSI related plots
           mpf.make_addplot(utils.calculateRSI(stock), panel=0, ylim=(0,100), color='#00ffe8', width=0.5),
           
           
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
           
           ]

mc = mpf.make_marketcolors(up='#9eff15', down='#ff1717', wick='w', volume='#00ffe8')
s = mpf.make_mpf_style(base_mpf_style='nightclouds',
                        marketcolors=mc,
                        figcolor='#07000d',
                        edgecolor='#5998ff')

fig, axlist = mpf.plot(df,
                style=s,
                type='candle',
                returnfig=True,
                xlabel='DATE',
                title=stock + ' Stock Data',
                addplot=apds,
                main_panel=1,
                num_panels=4)

ax_main = axlist[2]
ax_volu = axlist[0]
ax_emav = ax_main
ax_hisg = axlist[4]
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
    if (20+ival) > len(df):
        print('no more data to plot')
        ani.event_source.interval *= 3
        if ani.event_source.interval > 12000:
            exit()
        return
    data = df.iloc[0:(30+ival)]
    exp12     = data['Close'].ewm(span=12, adjust=False).mean()
    exp26     = data['Close'].ewm(span=26, adjust=False).mean()
    macd      = exp12 - exp26
    signal    = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal

    data['returns'] = data['Close'].pct_change()
    data['Up'] = np.maximum(data['Close'].diff(), 0)
    data['Down'] = np.maximum(-data['Close'].diff(), 0)
    data['RS'] = data['Up'].rolling(14).mean()/data['Down'].rolling(14).mean()
    rsi = 100 - 100/(1 + data['RS'])

    tr1 = pd.DataFrame(data['High'] - data['Low'])
    tr2 = pd.DataFrame(abs(data['High'] - data['Close'].shift()))
    tr3 = pd.DataFrame(abs(data['Low'] - data['Close'].shift()))
    tr = pd.concat([tr1, tr2, tr3], axis = 1).max(axis = 1)
    atr = tr.rolling(14).mean()

    plus_dm = data['High'].diff()
    minus_dm = data['Low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    negDI = abs(100 * (minus_dm.ewm(alpha = 1/14).mean() / atr))
    posDI = 100 * (plus_dm.ewm(alpha = 1/14).mean() / atr)

    directional_index = np.abs((posDI - negDI)/(posDI + negDI))
    adx = 100 * (directional_index.ewm(span=14, adjust=False).mean())

    data['rsi_lower'] = 30
    data['rsi_upper'] = 70
    data['adx_line'] = 25

    apds = [mpf.make_addplot(exp12, width=0.7, color='lime',ax=ax_emav, panel=1),
            mpf.make_addplot(exp26,color='c',ax=ax_emav, panel=1),
            mpf.make_addplot(histogram,type='bar',width=0.7,
                           color='dimgray',alpha=1,ax=ax_hisg, panel=2),
            mpf.make_addplot(macd,color='fuchsia',ax=ax_macd, panel=2),
            mpf.make_addplot(signal,color='b',ax=ax_sign, panel=2),

            mpf.make_addplot(rsi, panel=0, ylim=(0,100), color='#00ffe8', width=0.5, ax=ax_rsi),

            mpf.make_addplot(negDI, panel=3, ylim=(0, 100), width=0.7, ax=ax_negDI),
            mpf.make_addplot(posDI, panel=3, ylim=(0, 100), width=0.7, ax=ax_posDI),
            mpf.make_addplot(adx, panel=3, ylim=(0, 100), width=0.7, ax=ax_ADX),
           ]

    for ax in axlist:
        ax.clear()
    mpf.plot(data,type='candle',addplot=apds,ax=ax_main,main_panel=1,volume=ax_volu, num_panels=4)

ani = animation.FuncAnimation(fig,animate,interval=100)

mpf.show()