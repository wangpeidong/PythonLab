import finance
import math, sys
import numpy as np
import pandas as pd
import datetime
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from matplotlib import style

df = finance.sourcePrices(sys.argv[1])
df['HL_PCT'] = (df['High'] - df['Low']) / df['Adj Close'] * 100.0
df['PCT_change'] = (df['Adj Close'] - df['Open']) / df['Open'] * 100.0
df = df[['Adj Close', 'HL_PCT', 'PCT_change', 'Volume']]

forecast_col = 'Adj Close'
df.fillna(value = -99999, inplace = True)
forecast_out = 10 # 10 days
df['label'] = df[forecast_col].shift(-forecast_out)

X = np.array(df.drop(['label'], 1))
X = preprocessing.scale(X)
X_lately = X[-forecast_out:]
X_2nd_lately = X[-forecast_out:] 
X = X[:-forecast_out * 2] # Feature
y = np.array(df['label'][:-forecast_out * 2]) # Label

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)
#clf = svm.SVR()
clf = LinearRegression() # Classifier
clf.fit(X_train, y_train)
confidence = clf.score(X_test, y_test)
print(f'confidence: {confidence}')

last_col = len(df.columns)
df['Forecast'] = np.nan

# Comparing set with Adj Close using 2nd X_lately period feature
comparing_set = clf.predict(X_2nd_lately) 
for idx, val in enumerate(comparing_set):
    df.iloc[-forecast_out + idx, last_col] = val

# Future set based on X_lately period feature
forecast_set = clf.predict(X_lately)
last_date = df.iloc[-1].name
last_unix = last_date.timestamp()
one_day = 86400 # seconds in a day
next_unix = last_unix + one_day
for val in forecast_set:
    next_date = datetime.datetime.fromtimestamp(next_unix)
    next_unix += 86400
    df.loc[next_date, 'Forecast'] = val

df['Adj Close'].plot()
df['Forecast'].plot()
plt.legend(loc = 2)
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()


