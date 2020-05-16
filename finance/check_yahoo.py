import urllib.request
import os, time
import pandas as pd

def Check_Yahoo(stock_list):
    def end_point(symbol, category):
        return f'{symbol}/{category}?p={symbol}'

    yahoo_finance = 'http://finance.yahoo.com/quote/'    
    categories = ['key-statistics', 'financials', 'analysis', 'options']

    total = len(stock_list)
    count = 0
    for s in stock_list:
        try:
            for c in categories:
                link = yahoo_finance + end_point(s, c)
                print(link)
                
                resp = urllib.request.urlopen(link).read()

                file = f'yahoo/{s}_{c}.html'
                save = open(file, 'w')
                save.write(str(resp))
                save.close()
            count += 1
            print(f'{count}/{total} - {count/total:.0%}')
        except Exception as e:
            print(str(e))
            time.sleep(2)

if __name__ == '__main__':
    quotes = pd.read_csv('quotes.csv')
    Check_Yahoo(quotes['Symbol'])   