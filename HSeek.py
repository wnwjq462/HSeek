import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from Kiwoom import *
import time
from pandas import DataFrame
import datetime
import sqlite3
import pandas_datareader.data as web
import pandas as pd
import requests
import os
from bs4 import BeautifulSoup
from functools import reduce
import mpl_finance
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import gridspec
import numpy as np
import random
from multiprocessing import Process, Lock, Queue


MARKET_KOSPI = 0
MARKET_KOSDAQ = 10
TR_REQ_TIME_INTERVAL = 0.5

#미리 제작해놓은 ui 연결
BT_form_class = uic.loadUiType("backtesting.ui")[0]

#벡테스팅 시 벡테스팅 창에서 매도,매수를 각 종목을 클릭했을 때 표시되는 봉 차트를 구현하는 클래스
class Candle_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

#기본 창 setup
    def setupUI(self):
        self.setGeometry(300,300,1500,800)
        self.setWindowTitle("Candle Chart")

        self.fig = plt.Figure(figsize=(12,8))
        self.canvas = FigureCanvas(self.fig)

        self.tableWidget_4 = QTableWidget()
        self.tableWidget_4.setMaximumHeight(200)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.tableWidget_4)

        self.setLayout(layout)

#봉 차트 표시 함수
    def show_candel(self,df,buy_list_code,sell_list_code,end):

        print("Entrance")

        #이동평균선 구하고 저장
        ma5 = df['종가'].rolling(window=5).mean()
        ma20 = df['종가'].rolling(window=20).mean()
        ma60 = df['종가'].rolling(window=60).mean()
        df['MA5'] = ma5
        df['MA20'] = ma20
        df['MA60'] = ma60

        sold = False

        print(buy_list_code)
        buy_date = buy_list_code[2]
        buy_value = buy_list_code[0]
        #buy_index = buy_list_code[4]
        buy_index = df.loc[df['날짜'] == buy_date].index.values[0]
        buy_marker = df.iloc[buy_index]['고가']       #매수 지점 표시

        start_index = buy_index-5   #매수 지점 5일 전 부터 차트에 표시한다.
        end_index = df.loc[df['날짜'] == (end)]   #매도가 안된 경우에는 끝 지점이 벡 테스팅 마지막 날짜 기준으로 표시된다.
        end_index = end_index.index.values[0]

        #매도가 된 경우
        if buy_list_code[3] is True :
            sell_date = sell_list_code[2]
            sell_value = sell_list_code[0]
            sell_index = df.loc[df['날짜'] == str(sell_date), ['종가']]
            sell_index = sell_index.index.values[0]
            end_index = sell_index + 5      #매도 후 5일까지 차트에 표시
            sell_marker = df.iloc[sell_index]['고가']     #매도 지점 표시
            sold = True

        row = []
        pre_price = df.iloc[buy_index-1]['종가']
        pre_vol = df.iloc[buy_index-1]['거래량']
        cur_price = df.iloc[buy_index]['종가']
        cur_vol = df.iloc[buy_index]['거래량']
        p_rate = round((cur_price/pre_price-1)*100,2)
        v_rate = round((cur_vol/pre_vol-1)*100,2)

        row.append("매수")
        row.append(str(pre_price))
        row.append(str(pre_vol))
        row.append(str(cur_price))
        row.append(str(cur_vol))
        row.append(str(p_rate))
        row.append(str(v_rate))

        #매수, 매도에 대한 정보도 표로 정리하여 표시
        col_label = ["구분", "전날종가", "전날거래량", "당일종가", "당일거래량", "증감율", "거래대비"]
        self.tableWidget_4.setRowCount(1)
        self.tableWidget_4.setColumnCount(7)
        self.tableWidget_4.setHorizontalHeaderLabels(col_label)

        for i in range(len(row)) :
            item = QTableWidgetItem(row[i])
            self.tableWidget_4.setItem(0,i,item)

        if sold is True :
            row = []
            pre_price = df.iloc[sell_index - 1]['종가']
            pre_vol = df.iloc[sell_index - 1]['거래량']
            cur_price = df.iloc[sell_index]['종가']
            cur_vol = df.iloc[sell_index]['거래량']
            p_rate = round((cur_price / pre_price - 1) * 100, 2)
            v_rate = round((cur_vol / pre_vol - 1) * 100, 2)

            row.append("매도")
            row.append(str(pre_price))
            row.append(str(pre_vol))
            row.append(str(cur_price))
            row.append(str(cur_vol))
            row.append(str(p_rate))
            row.append(str(v_rate))

            self.tableWidget_4.setRowCount(2)

            for i in range(len(row)):
                item = QTableWidgetItem(row[i])
                self.tableWidget_4.setItem(1, i, item)

        new_df = df.loc[start_index : end_index]

        #날짜가 많으므로, 월요일만 표시
        day_list = new_df['날짜']
        dt_day_list = [datetime.datetime.strptime(v, "%Y%m%d").date() for v in day_list]
        new_day_list = []
        name_list = []
        b_marker_rate = ((new_df['종가'].max() / float(buy_value)) - 1) * 0.1

        for i, day in enumerate(dt_day_list):
            if day.weekday() == 0:
                new_day_list.append(i)
                name_list.append(str(day)[5:].replace('-', '/'))

        '''
        for i, day in enumerate(day_list):
            if str(day)[8:] == '0900':
                new_day_list.append(i)
                name_list.append(str(day)[4:8])
        '''

        '''if sold is True:
            print("sell_date", sell_date)
            print("iloc[-6]", day_list.iloc[-6])
        # fig = plt.figure(figsize = (12,8))'''
        #ax = plt.subplot2grid((4, 4), (0, 0), rowspan=3, colspan=4)
        spec = gridspec.GridSpec(ncols=1,nrows=2, height_ratios=[4,1])
        ax = self.fig.add_subplot(spec[0])

        #이동평균선 표시
        MA5_line, = ax.plot(day_list, new_df['MA5'], 'g', label='MA5')
        MA20_line, = ax.plot(day_list, new_df['MA20'], 'c', label='MA20')
        MA60_line, = ax.plot(day_list, new_df['MA60'], 'm', label='MA60')

        ax.plot(str(day_list.iloc[5]), buy_value * 1.01, 'v', markerfacecolor='black', markersize=12)
        ax.text(str(day_list.iloc[5]), buy_value * 1.02, 'buy', ha='center', va='center')

        if sold is True:
            ax.plot(str(day_list.iloc[-6]), sell_value * 1.01, 'v', markerfacecolor='black',
                    markersize=12)
            ax.text(str(day_list.iloc[-6]), sell_value * 1.02, 'sell', ha='center', va='center')

        #b_ax = plt.subplot2grid((4, 4), (3, 0), rowspan=1, colspan=4)
        b_ax = self.fig.add_subplot(spec[1])
        ax.xaxis.set_major_locator(ticker.FixedLocator(new_day_list))
        ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))
        b_ax.xaxis.set_major_locator(ticker.FixedLocator(new_day_list))
        b_ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))
        b_ax.bar(day_list, new_df['거래량'], label='Volume')       #거래량 그래프도 표시
        mpl_finance.candlestick2_ohlc(ax, new_df['시가'], new_df['고가'], new_df['저가'], new_df['종가'], width=0.5,
                                      colorup='r', colordown='b')

        self.fig.legend(fontsize=12)
        self.fig.tight_layout()
        # plt.show()
        self.canvas.draw()

#벡 테스팅 결과를 표시해주는 창을 구현하는 클래스
class BT_Window(QMainWindow, BT_form_class) :
    def __init__(self):
        super().__init__()
        self.btn_list1 = []
        self.btn1_num = 0
        self.btn_list2 = []
        self.btn2_num = 0
        self.setupUi(self)
        self.merge_list = []
        self.start_day = 0
        self.end_day = 0
        self.buy_list = {}
        self.sell_list = {}
        self.buy_df = {}
        self.candle_window = Candle_Window()


#벡 테스팅 창에서 종목 코드를 누르면 연결되는 이벤트 핸들러 -> 봉 차트를 표시한다.
    def candle_btn(self):
        sender = self.sender()
        code = sender.text()
        start = self.buy_list[code][2]
        end = self.end_day

        print("check 1")
        self.candle_window.__init__()
        print("check 2")
        print("buy_df[code]")
        print(self.buy_df[code])
        print("buy_list[code]")
        print(self.buy_list[code])
        if self.buy_list[code][3] is False :
            self.sell_list[code] = None
        print("sell_list[code]")
        print(self.sell_list[code])
        print("end :", end)
        self.candle_window.show_candel(self.buy_df[code],self.buy_list[code],self.sell_list[code],end)
        print("check 3")
        self.candle_window.show()
        print("check 4")


#벡 테스팅 결과를 표의 형식으로 보여줌
    def get_backtesting_result(self,buy_list,sell_list,start_value, money,start,end,buy_df):

        self.buy_df = buy_df
        self.start_day = start
        self.end_day = end
        self.buy_list = buy_list
        self.sell_list = sell_list
        print("sell_list len : ",len(sell_list))
        self.tableWidget_2.setRowCount(len(sell_list))
        for i,code in enumerate(sell_list):
            name = ("종목이름")
            buy_date = buy_list[code][2]
            buy_price = buy_list[code][0]
            buy_num = buy_list[code][1]
            sell_date = sell_list[code][2]
            sell_price = sell_list[code][0]
            sell_num = sell_list[code][1]
            sell_rate = sell_list[code][3]
            row = []
            row.append(name)
            row.append(code)
            row.append(str(int(buy_date)))
            row.append(str(int(buy_price)))
            row.append(str(buy_num))
            row.append(str(int(sell_date)))
            row.append(str(int(sell_price)))
            row.append(str(sell_num))
            row.append(str(round((sell_rate-1)*100,2))+"%")


            for j in range(len(row)):
                if j == 1 :
                    self.btn_list1.append(QPushButton(self.tableWidget_2))
                    self.btn_list1[self.btn1_num].setText(str(row[j]))
                    self.btn_list1[self.btn1_num].clicked.connect(self.candle_btn)
                    self.tableWidget_2.setCellWidget(i, j, self.btn_list1[self.btn1_num])
                    self.btn1_num += 1
                item = QTableWidgetItem(row[j])
                self.tableWidget_2.setItem(i,j,item)


        row_num = 0
        for code in buy_list :
            if buy_list[code][3] is False:
                row_num += 1

        self.tableWidget_3.setRowCount(row_num)

        n=0
        end_stock_value = 0
        total_value = 0

        for code in buy_list :
            if buy_list[code][3] is False :

                name = "분봉차트보기"

                b_row = []
                b_row.append(name)
                b_row.append(code)
                buy_date = buy_list[code][2]
                buy_price = buy_list[code][0]
                buy_num = buy_list[code][1]
                end_price = buy_list[code][5]
                end_stock_value += (end_price * buy_num)
                profit_rate = (end_price / buy_price - 1) * 100
                b_row.append(str(int(buy_date)))
                b_row.append(str(int(buy_price)))
                b_row.append(str(buy_num))
                b_row.append(str(end_price))
                b_row.append(str(round(profit_rate,2))+"%")

                for l in range(len(b_row)):
                    if l == 1:
                        self.btn_list2.append(QPushButton(self.tableWidget_3))
                        self.btn_list2[self.btn2_num].setText(str(b_row[l]))
                        self.btn_list2[self.btn2_num].clicked.connect(self.candle_btn)
                        self.tableWidget_3.setCellWidget(n, l, self.btn_list2[self.btn2_num])
                        self.btn2_num += 1
                    item = QTableWidgetItem(b_row[l])
                    self.tableWidget_3.setItem(n, l, item)

                n += 1


        total_value = end_stock_value + money
        total_rate = round(((total_value / start_value)-1) * 100,2)
        self.tableWidget_3.setRowCount(5)
        t_row = []
        t_row.append(str(start_value))
        t_row.append(str(round(money,2)))
        t_row.append(str(end_stock_value))
        t_row.append(str(round(total_value,2)))
        t_row.append(str(total_rate)+"%")

        for t in range(len(t_row)) :
            item = QTableWidgetItem(t_row[t])
            self.tableWidget.setItem(0,t,item)





#메인 클래스
class HSeek:
    def __init__(self):
        #self.kiwoom = Kiwoom()     #키움 API와 연결하는 부분 // 현재는 벡테스팅 기능에 집중하여 잠시 주석 처리
        #self.kiwoom.comm_connect()
        #self.get_code_list()
        self.today = datetime.datetime.today().strftime("%Y%m%d")
        #데이터 베이스 연결
        self.con_day_kospi = sqlite3.connect("c:/Users/H/Desktop/HTrader/HSeek/kospi_daydata.db")
        self.con_day_kosdaq = sqlite3.connect("c:/Users/H/Desktop/HTrader/HSeek/kosdaq_daydata.db")
        self.con_min_kopsi = sqlite3.connect("c:/Users/H/Desktop/HTrader/HSeek/kospi_mindata.db")

    #시장별로 종목 코드 리스트 받기
    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)
        self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)

    #종목 일봉 정보를 Dataframe에 저장
    def get_ohlcv(self,code,start):
        self.kiwoom.ohlcv = {'date': [], 'open':[], 'high' :[], 'low':[], 'close':[], 'volume':[]}

        self.kiwoom.set_input_value("종목코드",code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분",1)
        self.kiwoom.comm_rq_data("opt10081_req","opt10081",0,"0101")
        time.sleep(0.3)
        df = DataFrame(self.kiwoom.ohlcv, columns=['open','high','low','close','volume'],index=self.kiwoom.ohlcv['date'])

        return df

    #거래량 급증 종목 체크
    def check_speedy_rising_volume(self,code):
        df = self.get_ohlcv(code, self.today)
        volumes = df['volume']

        if len(volumes) < 21:   #거래량 데이터가 20개가 안되는 경우 제외
            return False

        sum_vol20 = 0
        today_vol = 0

        for i,vol in enumerate(volumes):
            if i == 0 :
                today_vol = vol
            elif i <= i <= 20:
                sum_vol20 += vol
            else:
                break

        avg_vol20 = sum_vol20 / 20
        if today_vol > avg_vol20*10:
            return True

    #HSeek 에서 찾은 종목을 buy_list.txt에 작성
    def update_buy_list(self,buy_list,reason):
        f = open("C:/Users/H/Desktop/HTrader/buy_list.txt","at",encoding='UTF8')
        for code in buy_list:
            f.writelines("매수;"+code+';'+self.kiwoom.get_master_code_name(code)+";시장가;10;0;매수전;"+reason+';\n')
        f.close()


    def seek_rising_volume(self,code_list):
        buy_list = []
        num = len(code_list)

        for i,code in enumerate(code_list):
            if self.check_speedy_rising_volume(code):
                buy_list.append(code)

        self.update_buy_list(buy_list,"거래량급증")
        print("complete")

    #종목별 분봉 데이터 저장
    def min_update(self):

        print("min_update start")
        start = time.time()
        code_list = os.listdir("c:/Users/H/Desktop/HTrader/HSeek/csv/kospi")

        for code in code_list :
            dir = "c:/Users/H/Desktop/HTrader/HSeek/csv/kospi/"
            dir = dir + code + "/min+1.csv"
            df = pd.read_csv(dir)
            df = df.rename(
                columns={'open': '시가', 'high': '고가', 'low': '저가', 'close': '종가', 'volume': '거래량', 'datetime': '시각'})
            price_rate_list = []
            volume_rate_list = []
            cum_volume_list = []
            cum_volume = 0
            table_name = "_" + code
            for i in range(len(df)):
                if i == 0:
                    cum_volume = df.iloc[0]['거래량']
                    price_rate = 0
                    volume_rate = 0
                    y_close = 0
                    y_volume = 0
                    price_rate_list.append(0)
                    volume_rate_list.append(0)
                    cum_volume_list.append(cum_volume)
                    date = str(df.iloc[i]['시각'])[4:8]
                    continue

                if str(df.iloc[i]['시각'])[4:8] != date:
                    cum_volume = df.iloc[i]['거래량']
                    date = str(df.iloc[i]['시각'])[4:8]
                    close = df.iloc[i]['종가']
                    y_close = df.iloc[i - 1]['종가']
                    y_volume = cum_volume_list[-1]
                    if y_close == '0' or y_close == 0:
                        price_rate = 0
                    else:
                        price_rate = float(close) / y_close
                        price_rate = (price_rate - 1) * 100
                        price_rate = round(price_rate, 2)

                    price_rate_list.append(price_rate)

                    if y_volume == '0' or y_volume == 0:
                        volume_rate = 0
                    else:
                        volume_rate = float(cum_volume) / y_volume
                        volume_rate = round(volume_rate, 2)

                    volume_rate_list.append(volume_rate)
                    cum_volume_list.append(cum_volume)

                else:
                    cum_volume += df.iloc[i]['거래량']
                    close = df.iloc[i]['종가']

                    if y_close == '0' or y_close == 0:
                        price_rate = 0
                    else:
                        price_rate = float(close) / y_close
                        price_rate = (price_rate - 1) * 100
                        price_rate = round(price_rate, 2)

                    if y_volume == '0' or y_volume == 0:
                        volume_rate = 0
                    else:
                        volume_rate = float(cum_volume) / y_volume
                        volume_rate = round(volume_rate, 2)

                    price_rate_list.append(price_rate)
                    volume_rate_list.append(volume_rate)
                    cum_volume_list.append(cum_volume)

            df['증감율'] = price_rate_list
            df['거래대비'] = volume_rate_list
            df['누적거래량'] = cum_volume_list
            column_list = ['시각', '시가', '고가', '저가', '종가', '거래량', '누적거래량', '증감율', '거래대비']
            df = df[column_list]
            df.to_sql(table_name, self.con_min_kopsi, if_exists='replace', index=False)


        print("min update completed")
        print("update time : ", time.time() - start)
        self.con_min_kopsi.commit()
        self.con_min_kopsi.close()

    #종목별 일봉 데이터 저장 // 상장일을 조사 후 web.DataReader 로 불러옴
    def day_update(self):

        print("Kospi_day_update start")
        start = time.time()

        cursor = self.con_day_kospi.cursor()
        cursor.execute("SELECT tbl_name FROM sqlite_master WHERE type = 'table'")
        table_list = cursor.fetchall()

        for code in self.kospi_codes :

            table_name = '_' + code
            '''
            table_check = False
            for name in table_list:
                name = str(name).replace('(', "")
                name = str(name).replace(')', "")
                name = str(name).replace("'", "")
                name = str(name).replace(',', "")
                if name == table_name:
                    table_check = True
                    break

            if table_check:
                continue
            '''
            url = "https://navercomp.wisereport.co.kr/v2/company/c1020001.aspx?cmp_cd="
            url = url + code + "&cn="
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            launch_day = soup.find_all('td', {'class': 'c2 txt'})
            launch_day = launch_day.__str__()
            launch_day = launch_day[launch_day.find("상장일") + 5:launch_day.find("상장일") + 15].replace("/", "")
            if launch_day == "":
                continue
            if int(launch_day) < 20000000 :
                launch_day = "20000104"
            print(code, " ", launch_day)

            err_flag = False
            try:
                df = web.DataReader(code + ".KS", 'yahoo', launch_day, datetime.datetime.today().strftime("%Y%m%d"))
            except:
                err_flag = True
                print("error occured - code : " + code)
                pass

            if err_flag :
                continue

            df = df.rename(columns={'Open': '시가', 'High': '고가', 'Low': '저가', 'Adj Close': '종가', 'Volume': '거래량'})
            del df['Close']
            price_rate_list = []
            volume_rate_list = []
            for i in range(len(df)):
                if i == 0:
                    price_rate_list.append(0)
                    volume_rate_list.append(0)
                    continue

                close = df.iloc[i]['종가']
                volume = df.iloc[i]['거래량']
                y_close = df.iloc[i - 1]['종가']
                y_volume = df.iloc[i - 1]['거래량']
                if y_close == '0' or y_close == 0:
                    price_rate = 0
                else:
                    price_rate = float(close) / y_close
                    price_rate = (price_rate - 1) * 100
                    price_rate = round(price_rate, 2)

                price_rate_list.append(price_rate)

                if y_volume == '0' or y_volume == 0:
                    volume_rate = 0
                else:
                    volume_rate = float(volume) / y_volume
                    volume_rate = round(volume_rate, 2)
                volume_rate_list.append(volume_rate)

            df['증감율'] = price_rate_list
            df['거래대비'] = volume_rate_list

            column_list = ['시가', '고가', '저가', '종가', '거래량', '증감율', '거래대비']
            df = df[column_list]
            new_index = df.index.strftime("%Y%m%d")
            ma5 = df['종가'].rolling(window=5).mean()
            ma20 = df['종가'].rolling(window=20).mean()
            ma60 = df['종가'].rolling(window=60).mean()
            ma120 = df['종가'].rolling(window=120).mean()
            df.insert(len(df.columns), "MA5", ma5)
            df.insert(len(df.columns), "MA20", ma20)
            df.insert(len(df.columns), "MA60", ma60)
            df.insert(len(df.columns), "MA120", ma120)

            df = df.reindex(new_index)
            df = round(df, 2)
            df.to_sql(table_name, self.con_day_kospi, if_exists='replace', index_label="날짜")



        print("Kospi Updated")
        print("update time : ", time.time() - start)
        self.con_day_kospi.commit()
        self.con_day_kospi.close()

        print("Kosdaq_day_update start")
        start = time.time()
        cursor = self.con_day_kosdaq.cursor()
        cursor.execute("SELECT tbl_name FROM sqlite_master WHERE type = 'table'")
        table_list = cursor.fetchall()
        for code in self.kosdaq_codes:
            table_name = '_' + code
            '''
            table_check = False
            for name in table_list:
                name = str(name).replace('(', "")
                name = str(name).replace(')', "")
                name = str(name).replace("'", "")
                name = str(name).replace(',', "")
                if name == table_name:
                    table_check = True
                    break

            if table_check:
                continue
            '''
            url = "https://navercomp.wisereport.co.kr/v2/company/c1020001.aspx?cmp_cd="
            url = url + code + "&cn="
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            launch_day = soup.find_all('td', {'class': 'c2 txt'})
            launch_day = launch_day.__str__()
            launch_day = launch_day[launch_day.find("상장일") + 5:launch_day.find("상장일") + 15].replace("/", "")

            url = "https://finance.naver.com/item/main.nhn?code="
            url = url + code
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            parse = soup.find_all('em', {'class': 'manage'})
            if parse :
                continue

            if launch_day == "":
                continue

            if int(launch_day) < 20000000 :
                launch_day = "20000104"

            print(code, " ", launch_day)
            #no_code_list = ["019590","035480","050320","052770","053950","054340","064520","065150","066790","079190","080530","085670","101000"]
            #if code in no_code_list :
            #    continue
            err_flag = False
            try:
                df = web.DataReader(code + ".KQ", 'yahoo', launch_day, datetime.datetime.today().strftime("%Y%m%d"))
            except:
                err_flag = True
                print("error occured - code : " + code)
                pass

            if err_flag :
                continue

            df = df.rename(columns={'Open': '시가', 'High': '고가', 'Low': '저가', 'Adj Close': '종가', 'Volume': '거래량'})
            del df['Close']
            price_rate_list = []
            volume_rate_list = []
            for i in range(len(df)):
                if i == 0:
                    price_rate_list.append(0)
                    volume_rate_list.append(0)
                    continue

                close = df.iloc[i]['종가']
                volume = df.iloc[i]['거래량']
                y_close = df.iloc[i - 1]['종가']
                y_volume = df.iloc[i - 1]['거래량']
                if y_close == '0' or y_close == 0:
                    price_rate = 0
                else:
                    price_rate = float(close) / y_close
                    price_rate = (price_rate - 1) * 100
                    price_rate = round(price_rate, 2)

                price_rate_list.append(price_rate)

                if y_volume == '0' or y_volume == 0:
                    volume_rate = 0
                else:
                    volume_rate = float(volume) / y_volume
                    volume_rate = round(volume_rate, 2)
                volume_rate_list.append(volume_rate)

            df['증감율'] = price_rate_list
            df['거래대비'] = volume_rate_list

            column_list = ['시가', '고가', '저가', '종가', '거래량', '증감율', '거래대비']
            df = df[column_list]
            new_index = df.index.strftime("%Y%m%d")
            ma5 = df['종가'].rolling(window=5).mean()
            ma20 = df['종가'].rolling(window=20).mean()
            ma60 = df['종가'].rolling(window=60).mean()
            ma120 = df['종가'].rolling(window=120).mean()
            df.insert(len(df.columns), "MA5", ma5)
            df.insert(len(df.columns), "MA20", ma20)
            df.insert(len(df.columns), "MA60", ma60)
            df.insert(len(df.columns), "MA120", ma120)
            df = round(df, 2)
            df = df.reindex(new_index)
            df.to_sql(table_name, self.con_day_kosdaq, if_exists='replace', index_label="날짜")



        print("Kosdaq Updated")
        print("update time : ", time.time() - start)
        self.con_day_kosdaq.commit()
        self.con_day_kosdaq.close()


    def db_update(self):
        #self.min_update()
        self.day_update()

    #어떠한 조건을 만족시킬 때 매수하는 함수
    def buy_func_1(self, code_list, merge_list, index,money, buy_list):


        for code in code_list :
            price_rate = '증감율' + '_' + code
            volume_rate = '거래대비' + '_' + code
            if merge_list.iloc[index][volume_rate] >= 3 and merge_list.iloc[index][price_rate] >= 10 :

                if code in buy_list :
                    continue

                price = merge_list.iloc[index]['종가'+'_'+code]
                date = merge_list.iloc[index]['날짜']
                num = 10

                if price * num > money :
                    return 0



                buy_list[code] = []
                buy_list[code].append(price)
                buy_list[code].append(num)
                buy_list[code].append(date)
                buy_list[code].append(False)
                buy_list[code].append(index)
                #buy_list[code].append(merge_list)
                return code

        return 0

    #어떤 조건을 만족시킬 때 매도하는 함수
    def sell_func_1(self, buy_list, merge_list, index, sell_list):

        for code in buy_list :
            price_rate = '증감율' + '_' + code
            buy_price = buy_list[code][0]
            cur_price = merge_list.iloc[index]['종가'+'_'+code]
            rate = cur_price/float(buy_price)
            date = merge_list.iloc[index]['날짜']

            if (rate <= 0.93 or rate >= 1.07) and buy_list[code][3] is False :
                buy_list[code][3] = True
                price = merge_list.iloc[index]['종가'+'_'+code]
                date = merge_list.iloc[index]['날짜']
                num = 10

                sell_list[code] = []
                sell_list[code].append(price)
                sell_list[code].append(num)
                sell_list[code].append(date)
                sell_list[code].append(rate)
                sell_list[code].append(index)
                return code

        return 0

    #buy_function, sell_function 기반으로 Back_testing 진행
    def back_testing(self, start, end, money, buy_func, sell_func, window):
        stock_value = 0
        total_value = money + stock_value
        start_value = total_value
        buy_list = {}
        sell_list = {}
        df_list = []
        buy_df = {}
        original_df_list = []


        #code_list = os.listdir("c:/Users/H/Desktop/HTrader/HSeek/csv/kospi")
        #con = sqlite3.connect("c:/Users/H/Desktop/HTrader/HSeek/kospi_mindata.db")
        con = sqlite3.connect("c:/Users/H/Desktop/HTrader/HSeek/kospi_daydata.db")


        sql = "SELECT name FROM sqlite_master WHERE type = 'table';"
        code_list = pd.read_sql(sql,con)
        code_list = code_list.values.tolist()
        code_list = [x.replace('_', '') for x in np.reshape(code_list, -1)]

        random.shuffle(code_list)
        code_list = code_list[0:30]
        #for i in range(10) :
            #code_list_list.append(code_list[90*i : 90*(1+i)])

        start_time = time.time()
        #DB로부터 일봉 정보를 불러오고, 모든 종목에 대해 비교하기 위해 Merge 시켜줌
        for code in code_list:
            sql = "SELECT * FROM "
            sql = sql + "_" + code
            close = "종가" + "_" + code
            price_rate = "증감율" + "_" + code
            volume_rate = "거래대비" + '_' + code
            open = "시가" + "_" + code
            high = "고가" + "_" + code
            low = "저가" + "_" + code
            volume = "거래량" + "_" + code
            MA5 = "MA5_" + code
            MA20 = "MA20_" + code
            MA60 = "MA60_" + code
            df = pd.read_sql(sql, con, index_col=None)
            #del df['시가']
            #del df['고가']
            #del df['저가']
            #del df['거래량']
            #del df['누적거래량']
            del df['MA120']

            original_df_list.append(df)
            #df = df.rename(columns={'종가': close, '증감율': price_rate, '거래대비': volume_rate})
            df = df.rename(columns={'종가': close, '증감율': price_rate, '거래대비': volume_rate, '시가':open,'고가':high, '저가':low, '거래량': volume, 'MA5' : MA5, 'MA20' : MA20, 'MA60' : MA60})
            df_list.append(df)
            #df_list = df_list[:100] #나중에 제거
            merge_list = reduce(lambda x, y: pd.merge(x, y, on='날짜', how='outer'), df_list)

        end_time = time.time()
        print("time : ", end_time - start_time)



        check = False #시작날짜 찾았는지의 여부

        #날짜를 하루씩 훑어가며 buy,sell 조건에 맞는 종목을 찾아감
        for i in range(len(merge_list)) :


            if int(merge_list.iloc[i]['날짜']) == int(start) :
                print("in")
                check = True

            if check :
                buy_code = self.buy_func_1(code_list,merge_list,i,money,buy_list)
                if buy_code != 0 :
                    print(str(len(buy_list))+"th stock bought" + "code : " + buy_code)
                    print(buy_list[buy_code])
                    money -= buy_list[buy_code][1] * buy_list[buy_code][0]      #buy_list[buy_code][0 : price 1: num 2: date ]
                    stock_value += buy_list[buy_code][1] * buy_list[buy_code][0]
                    end_price_col = '종가_' + str(buy_code)
                    end_price = merge_list.loc[merge_list['날짜'] == (end), [end_price_col]]
                    end_price = end_price.values[0][0]
                    buy_list[buy_code].append(end_price)
                    buy_df[buy_code] = original_df_list[code_list.index(buy_code)]
                    print("Buy Date : ", merge_list.iloc[i]['날짜'])
                    print("stock value :", stock_value)
                    print("money : ", money)
                    print("End Price: ", end_price)


                sell_code = self.sell_func_1(buy_list,merge_list,i, sell_list)
                if sell_code != 0:
                    money += (sell_list[sell_code][0] * sell_list[sell_code][1]) * 0.9967
                    stock_value -= sell_list[sell_code][0] * sell_list[sell_code][1]
                    print(str(len(sell_list))+"th stock sold" + "code : " + sell_code)
                    print(sell_list[sell_code])
                    print("Sell Date : ", merge_list.iloc[i]['날짜'])
                    print("stock value :", stock_value)
                    print("money : ", money)

                if int(merge_list.iloc[i]['날짜']) == int(end) :
                    print("out")
                    break

        total_value = stock_value + money
        print("value rate :", (float(total_value) / start_value) * 100)

        print("BackTesting Completed")
        print("Buy List (Not Sold) : ",end = " ")
        print(buy_list.keys())
        print("")
        print("Sell List : ", end = " ")
        print(sell_list.keys())
        print("Rate List : ", end = " ")
        print(sell_list.values())
        print("")
        window.get_backtesting_result(buy_list,sell_list,start_value,money,start,end,buy_df)





if __name__ == "__main__" :
    app = QApplication(sys.argv)
    hseek = HSeek()
    start = time.time()
    bt_window = BT_Window()
    hseek.back_testing("20180502","20180611",1000000,hseek.buy_func_1,hseek.sell_func_1, bt_window)
    bt_window.show()

    app.exec_()
    #hseek.db_update()



#hseek.seek_rising_volume(hseek.kosdaq_codes[:50])
