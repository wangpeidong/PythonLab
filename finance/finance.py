import datetime as dt
import pandas_datareader.data as web
import os.path as path
import numpy as np
import matplotlib.pyplot as plt

def plot_heatmap(data, columns, rows):
	fig, ax = plt.subplots()
	heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
	fig.colorbar(heatmap)
	ax.set_xticks(np.arange(data.shape[1]) + 0.5, minor=False)
	ax.set_yticks(np.arange(data.shape[0]) + 0.5, minor=False)
	ax.set_xticklabels(columns)
	ax.set_yticklabels(rows)
	ax.invert_yaxis()
	ax.xaxis.tick_top()
	plt.xticks(rotation=90)
	heatmap.set_clim(-1,1)
	for i in range(data.shape[1]):
		for j in range(data.shape[0]):
			ax.text(i+0.5, j+0.5, f'{data[i, j]:.2f}', ha="center", va="center", color="w")	
	plt.tight_layout()

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
            prc_df = pd.read_csv(ticker_file, index_col=0, parse_dates=True)
            #prc_df.set_index('Date', inplace=True)
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
	df['5-DMA'] = df['Adj Close'].rolling(window = 5, min_periods = 0).mean()
	df['10-DMA'] = df['Adj Close'].rolling(window = 10, min_periods = 0).mean()
	df['20-DMA'] = df['Adj Close'].rolling(window = 20, min_periods = 0).mean()

	# 6x1 grid, start at (0, 0), span 5 rows and 1 column
	ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan = 5, colspan = 1)
	# 6x1 grid, start at (5, 0), span 1 row and 1 column, align x axis with ax1
	ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan = 1, colspan = 1, sharex = ax1)

	df = df[-200:-1]
	idx = pd.to_datetime(df.index)

	ax1.plot(idx, df['Adj Close'])
	ax1.plot(idx, df['5-DMA'])
	ax1.plot(idx, df['10-DMA'])
	ax1.plot(idx, df['20-DMA'])
	ax2.bar(idx, df['Volume'])

	plt.xlabel('Trade Date')
	plt.show()

import mplfinance as mpf
def plotOHLC(ticker):
	# Load data file.
	df = sourcePrices(ticker)
	if df.empty:
		return

	df = df[-200:-1]
	 
	# Plot candlestick.
	# Add volume.
	# Add moving averages: 3,6,9.
	# Save graph to *.png.
	mpf.plot(df, type = 'candle', style = 'yahoo',
		title = ticker,
		ylabel = 'Price',
		ylabel_lower = 'Trade\nDate',
		volume = True, 
		mav = (5, 10, 20)) 
		#savefig = f'{ticker}.png')
