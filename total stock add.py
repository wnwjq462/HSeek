from pandas import DataFrame
import pandas_datareader.data as web
import pandas as pd
import requests
from bs4 import BeautifulSoup
from functools import reduce
import numpy as np
import sqlite3

con = sqlite3.connect("c:/Users/H/Desktop/HTrader/HSeek/kospi_daydata.db")


sql = "SELECT name FROM sqlite_master WHERE type = 'table';"
code_list = pd.read_sql(sql,con)
code_list = code_list.values.tolist()
code_list = [x.replace('_', '') for x in np.reshape(code_list, -1)]

market_size_1 = []
market_size_2 = []
market_size_3 = []
market_size_4 = []
market_size_5 = []


for code in code_list:
    table_name = '_' + code
    '''
    url = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd="
    url = url + code + "&cn="
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    market_cap = soup.find_all('td', {'class': 'num'})
    market_cap = market_cap.__str__()
    #market_cap = market_cap[market_cap.find("시가총액") + 5:market_cap.find("시가총액") + 15].replace("/", "")
    #print(market_cap)
    index_1 = market_cap.find("억원")
    #print(market_cap[index_1-5:index_1 + 2])
    #print(code)
    new_string = market_cap[index_1+5:]
    index_2 = new_string.find("억원")
    new_string_2 = (new_string[index_2-15:index_2+15])
    market_cap = (new_string_2.lstrip().rstrip())[:-2]
    '''
    sql = "SELECT * FROM "
    sql = sql + "_" + code
    df = pd.read_sql(sql, con, index_col=None)
    #print(type(int(df['시총'][0].replace(",", ""))))
    if not df['시총'][0] :
        continue
    market_cap = int(df['시총'][0].replace(",",""))
    if market_cap < 1000 :
        market_size_1.append(code)
    elif market_cap >= 1000 and market_cap < 5000 :
        market_size_2.append(code)
    elif market_cap >= 5000 and market_cap < 10000 :
        market_size_3.append(code)
    elif market_cap >= 10000 and market_cap < 100000 :
        market_size_4.append(code)
    else :
        market_size_5.append(code)


    '''
    if df.keys()[0] == "index" :
        print((df.keys())[0])
        print("has index code : " + code)
        del df['index']
        df.to_sql(table_name, con, if_exists='replace', index=None)
    '''
    #df['시총'] = market_cap

    #print(df)
    #del df['index']
    #df.to_sql(table_name, con, if_exists='replace', index = None)


print(len(market_size_1))
print(len(market_size_2))
print(len(market_size_3))
print(len(market_size_4))
print(len(market_size_5))
