from pandas import DataFrame
import pandas_datareader.data as web
import pandas as pd
import requests
from bs4 import BeautifulSoup
from functools import reduce
import numpy as np
import sqlite3
import time
from multiprocessing import Process, Lock, Queue
import multiprocessing
import datetime
import os
import logging


total_list = []
p_id = os.getpid()
pp_id = os.getppid()
MULTI_NUM = 5
range_list = [5,6,7,8,9,13,14,15,16,17,21,22,23,24,25,29,30,31,32,33]
con = sqlite3.connect("c:/Users/H/Desktop/HTrader/HSeek/kospi_daydata.db")
con_2 = sqlite3.connect("c:/Users/H/Desktop/HTrader/HSeek/kospi_daydata_2.db")

sql = "SELECT name FROM sqlite_master WHERE type = 'table';"
code_list = pd.read_sql(sql, con)
code_list = code_list.values.tolist()
code_list = [x.replace('_', '') for x in np.reshape(code_list, -1)]
today = datetime.datetime.today()
#print(today)

def multi(code,lock,q,start,end) :

    print("parent name: ", os.getppid())
    print("process id: ", os.getpid())
    past_date = "0"
    t = start
    total_list_m = []
    while True:
        print(t, end=" ")
        url = "https://finance.naver.com/item/frgn.nhn?code="
        url = url + code + "&page=" + str(t)
        t += 1
        if t == end + 1:
            print("end")
            break
        # print(url)
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')

        title = soup.select(
            '#content > div.section.inner_sub > table.type2 > tr:nth-child(5) > td.tc > span'
        )
        if len(title) == 0: break
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

        total_list_m += list


    #pf = DataFrame(total_list_m, columns=['날짜', '기관', '외국인'])
    #print(pf)


    lock.acquire()
    try:
        print("lock acquired")
        #shdata = q.get()
        #print(shdata)
        #shdata += total_list_m
        #print(shdata)

       #q.put(shdata)
    except :
        print("Error Occured")
    finally:
        print("lock released")
        lock.release()

    print("Proc End")




if __name__ == "__main__":

    for code in code_list[0:1]:

        code = "057050"
        print(code)
        shdata = []
        t = 1
        table_name = "_" + code
        sql = "SELECT * FROM "
        sql = sql + "_" + code
        df = pd.read_sql(sql, con, index_col=None)
        url = "https://navercomp.wisereport.co.kr/v2/company/c1020001.aspx?cmp_cd="
        url = url + code + "&cn="
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        launch_day = soup.find_all('td', {'class': 'c2 txt'})
        launch_day = launch_day.__str__()
        launch_day = launch_day[launch_day.find("상장일") + 5:launch_day.find("상장일") + 15].replace("/", "")
        print(launch_day)
        launch_day_datetime = datetime.datetime.strptime(launch_day, "%Y%m%d")
        print(launch_day_datetime)
        time_diff = (today - launch_day_datetime).days
        print(time_diff)
        if int(launch_day) < 20050103:
            total_page = 198
            print("total_page : ", total_page)
        else:
            print("else")
            total_page = int(((time_diff * 5) / 7) / 20)
            print(total_page)

        start_time = time.time()

        print("main process: ", os.getpid())
        lock = Lock()
        q = Queue()
        multiprocessing.log_to_stderr()
        logger = multiprocessing.get_logger()
        logger.setLevel(logging.DEBUG)
        q.put(shdata)
        proc1 = Process(target=multi, args=(code, lock, q, 1, 7))
        proc2 = Process(target=multi, args=(code, lock, q, 8, 14))
        proc3 = Process(target=multi, args=(code, lock, q, 15, 20))
        proc1.start()
        proc2.start()
        proc3.start()
        print("Here2")

        proc1.join()
        proc2.join()
        proc3.join()

        print("Here3")
        shdata = q.get()
        total_list = shdata
        print("check")
        pf = DataFrame(total_list, columns=['날짜', '기관', '외국인'])
        print(pf)







    #pf = DataFrame(total_list, columns=['날짜', '기관', '외국인'])
    #print(pf)

    #merge_df = pd.merge(df, pf, how='inner', on='날짜')
    #print(merge_df)
    end_time = time.time()
    print("total time : ", (end_time - start_time))
    #merge_df.to_sql(table_name, con_2, if_exists="replace", index=False)



print("Exit : ", os.getpid())
#total_list = total_list[0:8]

#con_2.commit()
#con_2.close()