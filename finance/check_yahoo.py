import urllib.request
import os, time, re
import pandas as pd
from datetime import datetime

categories = ('key-statistics', 'financials', 'analysis', 'options', 'profile')

def parse_Options(symbol):
    symbol_dir = f'yahoo/{symbol}'
    if not os.path.exists(symbol_dir):
        return []

    files = os.listdir(symbol_dir)
    if (len(files)) < 1:
        return []

    dfs = []
    for html_file in files:
        data = pd.read_html(f'{symbol_dir}/{html_file}')
        if not data:
            continue

        call = data[0]
        if call is not None and not call.empty:
            call['CallPut'] = 'call'
            call['Symbol'] = symbol

        if len(data) > 1:
            put = data[1]
            if put is not None and not put.empty:
                put['CallPut'] = 'put'
                put['Symbol'] = symbol

        dfs.extend(data)

    return dfs

def Create_OptionsSet(symbol_list):
    dfs = []
    total = len(symbol_list)
    count = 0
    for s in symbol_list:
        try:
            data = parse_Options(s)
            dfs.extend(data)

            count += 1
            print(f'{count}/{total} - {count/total:.0%}')

        except Exception as e:
            print(f'Exception: {str(e)} with symbol: {s}')

    df_combined = pd.concat(dfs, ignore_index=True)
    df_combined.to_csv(f'yahoo/Options.csv')

def parse_KeyStats(symbol):
    def trim_ending_number(field_name):
        f = re.split(r'\d+$', field_name)
        f = f[0].strip()
        return f

    def handle_field_with_Short(field_name):
        if not re.search('Short', field_name):
            return field_name

        f = re.split(r'\(', field_name)
        f = f[0].strip()
        return f

    html_file = f'yahoo/{symbol}_{categories[0]}.html'
    key_stats_list = pd.read_html(html_file)

    today = datetime.now().strftime('%Y%m%d')
    key_stats_dict = {'Date': [today], 'Symbol': [symbol]}

    for key_stats in key_stats_list:
        for i in range(len(key_stats)):
            nam = key_stats[0][i]
            nam = trim_ending_number(nam)
            nam = handle_field_with_Short(nam)
            val = key_stats[1][i] 
            key_stats_dict[nam] = [val] # Add as list so that we can extend later on

    #print(key_stats_dict)
    return key_stats_dict

def Create_KeyStatsSet(symbol_list):
    data_dict = None
    total = len(symbol_list)
    count = 0
    for s in symbol_list:
        try:
            data = parse_KeyStats(s)
            if not data_dict:
                data_dict = data
            else:
                for d in data:
                    data_dict[d].extend(data[d])

            count += 1
            print(f'{count}/{total} - {count/total:.0%}')

        except Exception as e:
            print(f'Exception: {str(e)} with symbol: {s}')

    df = pd.DataFrame.from_dict(data_dict)
    df.to_csv(f'yahoo/KeyStats.csv')

import bs4 as bs
def scrapOptions(symbol, link):
    try:
        source = urllib.request.urlopen(link).read()
        soup = bs.BeautifulSoup(source, 'lxml')
        scripts = soup.find_all('script')
        text = scripts[-5].text
        m_text = text.split(r'"expirationDates":[')
        if len(m_text) < 2:
            return

        n_text = m_text[1].split(r'],"hasMiniOptions"')
        expirationDates = n_text[0].split(',')
        if len(expirationDates) < 2:
            return

        symbol_dir = f'yahoo/{symbol}'
        if not os.path.exists(symbol_dir):
            os.makedirs(symbol_dir)
        for date in expirationDates:
            l = link + f'&date={date}'
            print(l)
            resp = urllib.request.urlopen(l).read()

            file = f'{symbol_dir}/{symbol}_{categories[3]}_{date}.html'
            save = open(file, 'w')
            save.write(str(resp))
            save.close()
    except Exception as e:
        print(f'Exception: {str(e)} with symbol: {symbol} to scrap Options')

def scrapProfile(symbol):
    try:
        html_file = f'yahoo/{symbol}_profile.html'
        with open(html_file) as source:
            soup = bs.BeautifulSoup(source, 'lxml')
            profile = [span.text for span in soup.body.find_all('span', class_='Fw(600)')]
            address = soup.body.find_all('p')[1].text

            profile.append(address)
            profile.insert(0, symbol)
        return profile
    except Exception as e:
        print(f'Exception: {str(e)} with symbol: {symbol} to scrap Profile')      

def Create_ProfileSet(symbol_list):
    total = len(symbol_list)
    count = 0
    profiles = {'Symbol':[], 'Sector':[], 'Industry':[], 'Employee':[], 'Address':[]}
    for symbol in symbol_list:
        profile = scrapProfile(symbol)
        profiles['Symbol'].append(profile[0])
        profiles['Sector'].append(profile[1])
        profiles['Industry'].append(profile[2])
        profiles['Employee'].append(profile[3])
        profiles['Address'].append(profile[4])
        count += 1
        print(f'{count}/{total} - {count/total:.0%}')

    df = pd.DataFrame(profiles)
    df.to_csv('yahoo/Profiles.csv')

def Check_Yahoo(symbol_list):
    def end_point(symbol, category):
        return f'{symbol}/{category}?p={symbol}'

    yahoo_finance = 'http://finance.yahoo.com/quote/'    

    total = len(symbol_list)
    count = 0
    for s in symbol_list:
        try:
            for c in categories:
                link = yahoo_finance + end_point(s, c)
                print(link)
                
                if c == categories[3]:
                    scrapOptions(s, link)
                else:
                    resp = urllib.request.urlopen(link).read()

                    file = f'yahoo/{s}_{c}.html'
                    save = open(file, 'w')
                    save.write(str(resp))
                    save.close()
            count += 1
            print(f'{count}/{total} - {count/total:.0%}')
        except Exception as e:
            print(f'Exception: {str(e)} with symbol: {s}')
            time.sleep(2)

from multiprocessing import Pool
import numpy as np
if __name__ == '__main__':
    quotes = pd.read_csv('quotes.csv')
    #with Pool(20) as p:
    #    p.map(Check_Yahoo, np.array_split(quotes['Symbol'], 10))   
    #Create_KeyStatsSet(quotes['Symbol'])
    #Create_OptionsSet(quotes['Symbol'])
    Create_ProfileSet(quotes['Symbol'])
