# HSeek

HSeek 프로그램은 어떠한 매수, 매도조건에 따라 백테스팅을 진행할 수 있고, 그 결과를 봉 차트와 수익율 등으로 보여준다.
또한 이러한 백 테스팅으로 여러 조건을 시험해 본후에는 수익을 낼 수 있는 알고리즘으로 매수, 매도를 해야할 종목들을 추천해주는 프로그램이다.

현재는 백테스팅을 구현한 상태이며, 최적의 알고리즘을 찾기 위해 백테스팅을 이용하여 여러 결과를 도출 해 볼 계획이다.

이 프로그램을 이용해서 구현할 계획들은 다음과 같다.

1. 거래량, 주가 증감율, 기관-외인 매수 매도 증감율을 다양한 조건으로 변화를 주며 백테스팅을 진행하여 최적의 조건을 찾기
2. 이동평균선 조건을 추가하고 이를 이용하여 조건식 찾아보기
3. 딥 러닝을 이용하여, 위의 값들을 Training 시켜서 최적의 조건 찾아보기
4. 여기에 뉴스 데이터를 추가하여 위의 모델과 융합시켜보기

다음은 HSeek의 DB 정보이다.

DataBase 이름 kospi_(kosdaq_)mindata_year(연단위)

Table
종목코드 -> 여러개

index : min

column: 현재가 거래량 누적거래량 거래대비 증감율
연별로 분봉을 담아놓는 데이터베이스

DataBase 이름 kospi_(kosdaq)daydata

Table
종목코드 -> 여러개

index : day

column : 현재가 거래량 시가 고가 저가 전일대비주가 전일대비거래량
전체연도의 일봉을 담아놓는 데이터베이스

다음은 지금까지 HSeek.py 속 구현한 함수들에 대한 Manual 이다.

* HSeek.py

HSeek 클래스

__init__(self) : 키움 API와 DB와 연결한다.

get_code_list(self) : 시장별로 종목 코드 리스트 받기

get_ohlcv(self,code,start) : 종목 일봉 정보를 Dataframe에 저장

check_speedy_rising_volume(self,code) : 거래량 급증 종목 체크

update_buy_list(self,buy_list,reason) : HSeek 에서 찾은 종목을 buy_list.txt에 작성

min_update(self) : 종목별 분봉 데이터 저장 - 여기서는 분봉데이터를 csv 파일로 받아놓은 것을 DataFrame으로 변환한 후 DB에 저장하였다.

day_update(self) : 종목별 일봉 데이터 저장 - 상장일을 스크래핑한 후에 상장일로부터 현재일자까지 web.DataReader 로 일봉 데이터를 불러와 저장하였다.

buy_func_1(self, code_list, merge_list, index,money, buy_list) : 어떠한 조건을 만족시킬 때 매수하는 함수 - 현재는 증감율과 거래량 기준으로 구현하였다. 

여기서 buy_list 딕셔너리가 나오는데 이 딕셔너리에 대한 정보는 다음과 같다

list[0] = price
list[1] = num
list[2] = date 로 바꿔주기
list[3] = 팔렸는지 여부 (sold) 팔리면 True 안팔렸으면 False
list[4] = merge list 의 index
list[5] = end price 백테스팅 종료시의 가격

sell_func_1(self, buy_list, merge_list, index, sell_list) : 어떤 조건을 만족시킬 때 매도하는 함수 - 이것은 현재 증감율과 구입시가격과 현재 가격의 비율을 통해 구현하였다.

여기서 sell_list 딕셔너리는 다음과 같은 요소를 가진다.

list[0] = price
list[1] = num
list[2] = date
list[3] = rate 판매한 증감율
list[4] = merge list 의 index

back_testing(self, start, end, money, buy_func, sell_func, window) : buy_function, sell_function 기반으로 Back_testing 진행한다. 
DB로 부터 일봉 정보를 불러오고, 모든 종목에 대해 비교해야 하기 때문에 각 종목들의 DataFrame 을 Merge 시켜주었다. 그 후 입력 받은 백테스팅 초기 일자부터 시작하여 매수,매도 조건을 만족하는 종목이 있는지 찾는다. 그러한 종목들은 buy_list, sell_list에 매수 날짜, 가격 등의 정보와 함께 저장해준다.



BT_Window 클래스

이 클래스는 백테스팅 결과를 표시해주는 창을 구현했다. 위의 back_testing 에서 얻은 buy_list, sell_list를 이용하여 백 테스팅 결과를 표시해준다. 

candle_btn(self) : 백 테스팅 창에서 종목 코드를 누르면 연결되는 이벤트 핸들러 -> 봉 차트를 표시한다.

get_backtesting_result(self,buy_list,sell_list,start_value, money,start,end,buy_df) : 백 테스팅 결과를 표의 형식으로 보여줌, 이 표에서 매수 시각, 가격, 수량, 수익률 등을 확인할 수 있다.


Candle_Window 클래스

이 클래스는 BT_Window 창에서 결과로 나온 매수, 매도 종목의 코드 버튼을 눌렀을 때 각 종목에 대한 봉 차트를 보여주는 클래스이다.

show_candel(self,df,buy_list_code,sell_list_code,end) : 봉 차트 표시 함수

여기서 이동평균선을 구하고, 매수 지점, 매도 지점을 확인하여 각 지점으로부터 5일 전, 후까지를 봉차트에 표시한다.
그 봉차트 아래에는 각 날짜에 해당하는 거래량 데이터도 막대 그래프로 나타낸다.
또한 매수, 매도 지점을 봉 차트에서 화살표로 표시해주었다.




