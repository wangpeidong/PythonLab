import datetime as dt
import pandas_datareader.data as web
import os.path as path

start_date = dt.datetime(2015, 1, 2)
end_date = dt.datetime.now()

import pandas as pd
# Source price for a given ticker
def sourcePrices(ticker):
    tickerFile = f'prices/{ticker}.csv'
    prcDf = pd.DataFrame()
    try:
        if path.exists(tickerFile):
            print(f'{ticker} sourced already')
            prcDf = pd.read_csv(tickerFile)
            prcDf.set_index('Date', inplace=True)
        else:
            prcDf = web.DataReader(ticker, 'yahoo', start_date, end_date)
            prcDf.to_csv(tickerFile)
            print(f'sourcing {ticker}')
    except Exception as e:
        print(f'Exception: {str(e)}')
    return prcDf

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

# Level price to compare Apple to Pearl
from sklearn.preprocessing import StandardScaler
def levelPrice(df):
    scaledDf = StandardScaler().fit_transform(df)
    for ind, column in enumerate(df.columns):
        df[column] = scaledDf[:,ind]
    return df

# Source my portfolio
#df = pd.read_csv("quotes.csv")
#tickers = df['Symbol'].drop_duplicates()

# Source benchmark
benchmarks = pd.Series(['^GSPC', '^IXIC', '^DJI'])
    
import sys
print(sys.argv[1:])
df = levelPrice(combineAdjClose(benchmarks.append(pd.Series(sys.argv[1:]))))

# Plot data frame
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot') 
df[-50:-1].plot()
plt.show()


