import datetime as dt
import pandas_datareader.data as web
import os.path as path

start_date = dt.datetime(2015, 1, 2)
end_date = dt.datetime.now()

import pandas as pd
# Source price for a given ticker
def sourcePrices(ticker):
    ticker_file = f'prices/{ticker}.csv'
    prc_df = pd.DataFrame()
    try:
        if path.exists(ticker_file):
            print(f'{ticker} prices sourced already')
            prc_df = pd.read_csv(ticker_file)
            prc_df.set_index('Date', inplace=True)
        else:
            prc_df = web.DataReader(ticker, 'yahoo', start_date, end_date)
            prc_df.to_csv(ticker_file)
            print(f'sourcing {ticker} prices')
    except Exception as e:
        print(f'Exception: {str(e)}')
    return prc_df

# Combine multiple tickers 'Adj Close' into the same data frame
def combineAdjClose(tickers):
    main_df = pd.DataFrame()
    for ticker in tickers:
        df = sourcePrices(ticker)
        if df.empty:
            continue
        
        df.rename(columns = {'Adj Close': ticker}, inplace = True)
        df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace = True)
        
        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')
        
    print(main_df.tail())
    return main_df

# Scale price to leveling for Apple to Pearl comparation
from sklearn.preprocessing import StandardScaler
def levelPrice(df):
    scaled_df = StandardScaler().fit_transform(df)
    for ind, column in enumerate(df.columns):
        df[column] = scaled_df[:,ind]
    return df

# Consolidate portfolio quotes to sum quantity per ticker (Multiple lots ticker has multiple quotes)
# return dictionary[ticker, quantity]
def consolidateQuotes():
    tickers = {}
    try:
        df = pd.read_csv('quotes.csv')
        for ticker, qty in zip(df['Symbol'], df['Quantity']):
            if ticker not in tickers:
                tickers[ticker] = qty
            else:
                tickers[ticker] += qty
    except Exception as e:
        print(f'Exception: {str(e)}')

    print(f'{len(tickers)} tickers out of {len(df)} quotes consolidated ')
    return tickers

# Evaluate portfolio average Adj Close price
# Input: dictionary[ticker, quantity]
def evalPortfolio(tickers):
    main_df = pd.DataFrame()
    for ticker in tickers:
        df = sourcePrices(ticker)
        if df.empty:
            continue

        if main_df.empty:
            main_df = df
            main_df['Volume'] = tickers[ticker]
        else:
            main_df['Adj Close'] = main_df['Adj Close'] * main_df['Volume'] + df['Adj Close'] * tickers[ticker]
            main_df['Volume'] += tickers[ticker]
            main_df['Adj Close'] /= main_df['Volume']

    main_df.rename(columns = {'Adj Close': 'Portfolio'}, inplace = True)
    main_df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace = True)

    print(main_df.tail())
    return main_df

import matplotlib.pyplot as plt
# Plot DMA 200, 50, 20 for a given ticker
def plotDMA(ticker):
	df = sourcePrices(ticker)
	if df.empty:
		return
	df['200-DMA'] = df['Adj Close'].rolling(window = 200, min_periods = 0).mean()
	df['50-DMA'] = df['Adj Close'].rolling(window = 50, min_periods = 0).mean()
	df['20-DMA'] = df['Adj Close'].rolling(window = 20, min_periods = 0).mean()

	# 6x1 grid, start at (0, 0), span 5 rows and 1 column
	ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan = 5, colspan = 1)
	# 6x1 grid, start at (5, 0), span 1 row and 1 column, align x axis with ax1
	ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan = 1, colspan = 1, sharex = ax1)

	df = df[-200:-1]
	ax1.plot(df.index, df['Adj Close'])
	ax1.plot(df.index, df['200-DMA'])
	ax1.plot(df.index, df['50-DMA'])
	ax1.plot(df.index, df['20-DMA'])
	ax2.bar(df.index, df['Volume'])
