import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.cluster import KMeans, MeanShift
from sklearn.model_selection import train_test_split
from sklearn import preprocessing

def numerical_text(text_col):
	text_num_dict = {}
	texts = text_col.values.tolist()
	# finding just the uniques
	unique_texts = set(texts)
	n = 0
	for unique in unique_texts:
		if unique not in text_num_dict:
			# creating dict that map text to number
			text_num_dict[unique] = n
			n += 1

	return text_col.apply(lambda x: text_num_dict[x])

df = pd.read_csv('yahoo/Options.csv', index_col=0, dtype=str)
df.drop(['Contract Name', 'Last Trade Date'], axis=1, inplace=True)
df = df.apply(lambda x: x.str.replace(',', ''))
df.replace('-', 0, inplace=True)
call_put = {'call': 0, 'put': 1}
df['CallPut'] = df['CallPut'].apply(lambda x: call_put[x])
df['% Change'] = df['% Change'].str.rstrip('%').astype('float')/100.0
df['Implied Volatility'] = df['Implied Volatility'].str.rstrip('%').astype('float')/100.0
df['Symbol'] = numerical_text(df['Symbol'])
df.fillna(0, inplace=True)
df.astype('float').dtypes
#df.to_csv('yahoo/test.csv')

X = np.array(df)
X = preprocessing.scale(X)

#clf = KMeans(n_clusters=2)
clf = MeanShift()
clf.fit(X)

from collections import Counter
print(Counter(clf.labels_))
print(len(np.unique(clf.labels_)))

