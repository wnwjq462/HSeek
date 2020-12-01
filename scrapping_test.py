from pandas import DataFrame
import pandas_datareader.data as web
import pandas as pd
import requests
from bs4 import BeautifulSoup
from functools import reduce
import numpy as np
import sqlite3
import time


total_list = []
range_list = [5,6,7,8,9,13,14,15,16,17,21,22,23,24,25,29,30,31,32,33]
con = sqlite3.connect("c:/Users/H/Desktop/HTrader/HSeek/kospi_daydata.db")
con_2 = sqlite3.connect("c:/Users/H/Desktop/HTrader/HSeek/kospi_daydata_2.db")

sql = "SELECT name FROM sqlite_master WHERE type = 'table';"
code_list = pd.read_sql(sql, con)
code_list = code_list.values.tolist()
code_list = [x.replace('_', '') for x in np.reshape(code_list, -1)]

for code in code_list[0:4] :
    past_date = "0"
    #code = "000040"
    print(code)
    t = 1

    table_name = "_" + code
    sql = "SELECT * FROM "
    sql = sql + "_" + code
    df = pd.read_sql(sql, con, index_col=None)
    start_time = time.time()
    while True:

        print(t,end=" ")
        url = "https://finance.naver.com/item/frgn.nhn?code="
        url = url + code + "&page=" + str(t)
        t += 1
        # if t == 23 : break
        # print(url)
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')

        title = soup.select(
            '#content > div.section.inner_sub > table.type2 > tr:nth-child(5) > td.tc > span'
        )
        if len(title) == 0 : break
        cur_date = title[0].text

        if past_date == cur_date: break

        past_date = title[0].text
        list = [[0] * 3 for i in range(20)]

        for i in range_list:
            index = 0
            if int(i / 5) == 1:
                index = i - 5
            elif int((i - 3) / 5) == 2:
                index = i - 8
            elif int((i - 1) / 5) == 4:
                index = i - 11
            else:
                index = i - 14

            selector = '#content > div.section.inner_sub > table.type2 > tr:nth-child('
            selector = selector + str(i) + ') > td.tc > span'
            title = soup.select(
                selector
            )

            if len(title) == 0: break

            cur_date = title[0].text.replace(".", "")
            list[index][0] = cur_date

            selector = '#content > div.section.inner_sub > table.type2 > tr:nth-child('
            selector = selector + str(i) + ') > td:nth-child(6) > span'
            title = soup.select(
                selector
            )

            list[index][1] = title[0].text

            selector = '#content > div.section.inner_sub > table.type2 > tr:nth-child('
            selector = selector + str(i) + ') > td:nth-child(7) > span'
            title = soup.select(
                selector
            )

            list[index][2] = title[0].text

            # print(list[index][0] + " " + list[index][1] + " " + list[index][2])

            # print(pf)

        total_list += list
    print("")

    pf = DataFrame(total_list, columns=['날짜', '기관', '외국인'])
    #print(pf)

    merge_df = pd.merge(df, pf, how='inner', on='날짜')
    #print(merge_df)
    end_time = time.time()
    print("total time : ", (end_time - start_time))
    merge_df.to_sql(table_name, con_2, if_exists="replace", index=False)




#total_list = total_list[0:8]

con_2.commit()
con_2.close()
