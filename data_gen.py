import yfinance as yf
import pandas as pd
import time

stock = 'AAPL'
while True:
    data = yf.download(tickers=stock, period='1d', interval='1m')
    data.to_csv(stock + '.csv')

    time.sleep(1)