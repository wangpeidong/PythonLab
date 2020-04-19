import datetime as dt
import pandas_datareader.data as web
import os.path as path

start_date = dt.datetime(2015, 1, 2)
end_date = dt.datetime.now()

# Source price for given tickers
def sourcePrices(tickers):
    for ticker in tickers:
        if path.exists(f'prices/{ticker}.csv'):
            print(f'{ticker} sourced already')
            pass
        else:
            df = web.DataReader(ticker, 'yahoo', start_date, end_date)
            df.to_csv(f'prices/{ticker}.csv')
            print(f'sourcing {ticker}')
    print(f'---sourced {len(tickers)} tickers---')

import pandas as pd
# Source benchmark 
benchmarks = pd.Series(['^GSPC', '^IXIC', '^DJI'])
#sourcePrices(benchmarks)

# Source my portfolio
df = pd.read_csv("quotes.csv")
tickers = df['Symbol'].drop_duplicates()
#sourcePrices(tickers)

# Combine multiple tickers 'Adj Close' into the same data frame
def combineAdjClose(tickers):       
    main_df = pd.DataFrame()
    for ticker in tickers:
        df = pd.read_csv(f'prices/{ticker}.csv')
        df.set_index('Date', inplace=True)
        
        df.rename(columns = {'Adj Close': ticker}, inplace = True)
        df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace = True)
        
        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')
        print(f'append {ticker}')
        
    print(main_df.head())
    print(main_df.tail())
    return main_df

# Level price to compare Apple to Pearl
from sklearn.preprocessing import StandardScaler
def levelPrice(df):
    scaledDf = StandardScaler().fit_transform(df)
    for ind, column in enumerate(df.columns):
        df[column] = scaledDf[:,ind]
    return df
    
import sys
begin =  int(sys.argv[1])
end = int(sys.argv[2])
df = levelPrice(combineAdjClose(benchmarks.append(tickers[begin:end])))

# Plot data frame
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot') 
df[-50:-1].plot()
plt.show()


