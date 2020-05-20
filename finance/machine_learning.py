import numpy as np
import pandas as pd
from sklearn import svm, neighbors
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.cluster import KMeans, MeanShift
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from collections import Counter

def numerical_date(date):
	if not isinstance(date, str):
		return date

	date = date.strip()
	if date == '':
		return ''

	import time
	try:
		date = time.strptime(date, '%d-%b-%y')
		date = str(time.mktime(date))
	except Exception as e:
		pass	

	return date	

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

def ml_options():
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

	print(Counter(clf.labels_))
	print(len(np.unique(clf.labels_)))

def norm_numerical(number):
	if not isinstance(number, str):
		return number

	import re
	number = number.strip()
	multipliers = {'k':1000.00, 'K':1000.00, 
				   'm':1000000.00, 'M':1000000.00, 
				   'b':1000000000.00, 'B':1000000000.00, 
				   't':100000000000.00, 'T':100000000000.00,
				   '%':0.01}
	mul = 1
	if re.search(r'[k|K|m|M|b|B|t|T|%]$', number):
		mul = multipliers[number[-1:]]
		number = number[:-1]
	# return if there are one or more letters
	if re.search(r'[a-zA-Z]+', number):
		return number
	number = number.replace(',', '')

	try:
		nms = number.split(':')
		if len(nms) == 2:
			number = float(nms[0]) / float(nms[1])
		else:
			number = float(number) * mul
		number = str(number)
	except Exception as e:
		pass

	return number

def ml_keystats():
	# preparing data to feed machine
	df = pd.read_csv('yahoo/KeyStats.csv', index_col=0)
	df.drop(['mean', 'std', 'min', '25%', '50%', '75%', 
			'S&P500 52-Week Change', 'Fiscal Year Ends', 'Most Recent Quarter (mrq)'
			], axis=1, inplace=True)
	df['Dividend Date'] = df['Dividend Date'].apply(lambda x: numerical_date(x))
	df['Ex-Dividend Date'] = df['Ex-Dividend Date'].apply(lambda x: numerical_date(x))
	df['Last Split Date'] = df['Last Split Date'].apply(lambda x: numerical_date(x))
	df = df.applymap(norm_numerical) # apply works for column/row only
	df.Sector = numerical_text(df.Sector)
	df.Industry = numerical_text(df.Industry)
	df.Country = numerical_text(df.Country)
	
	df.astype('float').dtypes

	df['Target'] = df['Current Price'] > df['Purchase Price']
	df.Target = df.Target.apply(lambda x: int(x))
	df.drop(['Current Price', 'Purchase Price'], axis=1, inplace=True)
	df.fillna(-999999999999, inplace=True)

	X = np.array(df.drop(['Target'], 1))
	y = np.array(df['Target'])

	# doing machine learning
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

	clf = VotingClassifier([('lsvc', svm.LinearSVC()),
							('knn', neighbors.KNeighborsClassifier()),
							('rfor', RandomForestClassifier())])	

	clf.fit(X_train, y_train)
	confidence = clf.score(X_test, y_test)
	print('accuracy:', confidence)
	predictions = clf.predict(X_test)
	print('predicted class counts:', Counter(predictions))
	return confidence	

def unit_test():
	test = ['-3,750.73%', '-97.08M', '1.12', 'ABC', '40,586', '-0.2353388', '2.8B', '1:08']
	[print(norm_numerical(t)) for t in test]
	date = '7-Dec-19'
	print(numerical_date(date))

if __name__ == '__main__':
	ml_keystats()
