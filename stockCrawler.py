# 인베스팅 데이터 갖고오기
# https://pypi.org/project/investpy/
# pip install investpy==0.9.12

# 구글에서 갖고오기는 막힌듯... 야후에서 갖고와야...
# https://finance.yahoo.com/quote/CL=F?p=CL=F
# pip install yfinance

import pandas as pd 
from pandas import DataFrame

import urllib.request
from bs4 import BeautifulSoup
import yfinance as yf

from datetime import datetime
from datetime import timedelta

#----------------------------------------------------------#
# 주식 목록 갖고오기 (상위)
class StockCrawler:
    def __get_naver_url_code(self, ticker):    
        url = 'http://finance.naver.com/item/sise_day.nhn?code={ticker}'.format(ticker=ticker)
        print("요청 URL = {}".format(url))
        return url

    # 종목 이름을 입력하면 종목에 해당하는 코드를 불러와 
    def __get_naver_stock_url(self, item_name, stockDf):
        ticker = stockDf.query("name=='{}'".format(item_name))['ticker'].to_string(index=False)
        url = self.__get_naver_url_code(ticker)
        return url

    def get_korea_stock_data_from_naver(self, ticker, loadDays):
        # 일자 데이터를 담을 df라는 DataFrame 정의
        df = pd.DataFrame()
        try:
            url = self.__get_naver_url_code(ticker)
            loadDays = (loadDays / 10) + 1
            # 1페이지가 10일. 100페이지 = 1000일 데이터만 가져오기 
            for page in range(1, int(loadDays)):
                pageURL = '{url}&page={page}'.format(url=url, page=page)
                df = df.append(pd.read_html(pageURL, header=0)[0], ignore_index=True)
            
            # df.dropna()를 이용해 결측값 있는 행 제거 
            df = df.dropna()
            df.reset_index(inplace=True, drop=False)
            stockDf = pd.DataFrame(df, columns=['날짜', '시가', '고가', '저가', '종가', '거래량'])
            stockDf.rename(columns={'날짜': 'Date', '고가': 'High', '저가': 'Low', '시가': 'Open', '종가': 'Close', '거래량' : 'Volume'}, inplace = True)
            stockDf['Date'] = stockDf['Date'].str.replace(".", "-")
            
            print(stockDf)
            return stockDf
        except:
            return None
    
    def get_stock_data(self, ticker, loadDays):
        oldDate = datetime.now() - timedelta(days=loadDays)
        strtdDate = oldDate.strftime("%Y-%m-%d")
        endDate = datetime.now().strftime("%Y-%m-%d")

        try:
            df = yf.download(ticker, strtdDate, endDate)
            if not df.empty:
                df.reset_index(inplace=True, drop=False)
                df['Date'] = pd.to_datetime(df.Date, format='%Y-%m-%d')

                features =['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                df = df[features]
                return df
            return None
        
        except:
            print("[%s] Ticker load fail" % ticker)
            return None

    def get_recommand_stocks(self):
        url = "https://finance.naver.com/sise/lastsearch2.nhn"
        req = urllib.request.urlopen(url)
        res = req.read()
        
        soup = BeautifulSoup(res,'html.parser') # BeautifulSoup 객체생성
        table = soup.find('table', {'class': 'type_5'})
        trs = table.find_all('tr')

        recomands = []
        for idx, tr in enumerate(trs): # enumerate를 사용하면 해당 값의 인덱스를 알 수 있다.
            if idx > 0:
                tds = tr.find_all('td')
                if len(tds) > 2:
                    stockName = tds[1].text.strip()
                    recomands.append(stockName)
      
        return recomands

    def _load_from_file(self, targetList):
        stockDf = DataFrame(columns = ("name", "ticker", "ranking"))
        for text in targetList:
            tokens = text.split(':')
            new_row = {'name': tokens[0], 'ticker': tokens[1], 'ranking': tokens[2]}
            stockDf.loc[-1] = new_row
            stockDf = stockDf.reset_index(drop=True)
        return stockDf

    def get_stocks_list_from_file(self, fileName):
        with open(fileName, "r", encoding="utf-8") as f:
            targetList = f.read().splitlines()
        return self._load_from_file(targetList)

#----------------------------------------------------------#
class USAStockCrawler(StockCrawler):
   # s&p 500, 나스닥 갖고 오기
    def get_stock_list(self, limit, debug = False):
        sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        sp500 = sp500[['Security', 'Symbol']] 
        sp500 = sp500.rename(columns={'Security': 'name', 'Symbol': 'ticker'})
        
        nasdaqDf = pd.read_html("https://en.wikipedia.org/wiki/NASDAQ-100#External_links")[3]
        nasdaqDf = nasdaqDf.rename(columns={'Company': 'name', 'Ticker': 'ticker'})

        sp500.loc[-1] = nasdaqDf
        stockDf = sp500
        stockDf = stockDf.drop_duplicates(['ticker'], keep='last')
        # 시총 구하기
        marketCapList = []
        ranking = []
        dropIdx = []
        for idx, row in stockDf.iterrows():
            try:
                if debug == False:
                    tickers = row['ticker']
                    p = web.get_quote_yahoo(tickers)['marketCap']
                    marketCap = int(p.values[0])
                    marketCapList.append(marketCap)
                else:
                    marketCapList.append(idx)
            except:
                dropIdx.append(idx)
                marketCapList.append(0)
                print("[%s][%s] 시총 갖고오기 에러" % (row['name'], row['ticker']))
        
        rank = 1
        for i in marketCapList:
            ranking.append(rank)
            rank += 1

        stockDf['MarketCap'] = marketCapList
        stockDf = stockDf.sort_values(by='MarketCap', ascending=False)
        stockDf['ranking'] = ranking

        stockDf.drop(dropIdx, inplace = True)
        if limit > 0:
            stockDf = stockDf[:limit]
        
        print(stockDf)
        return stockDf

#----------------------------------------------------------#
### 구글이 안되니 아후에서 긁자.
class KoreaStockCrawler(StockCrawler):
    def get_stock_data(self, ticker, loadDays):
        rowTicker = ticker
        try:
            # 코스피는 KS, 코스닥은 KQ, 지수는 앞에 ^
            if ticker[0] == '^':
                t = ticker                
            else:
                t = ticker + ".KS"            

            df = super().get_stock_data(t, loadDays)
            if df == None:
                t = ticker + ".KQ"            
                df = super().get_stock_data(t, loadDays)
            return df

        except:
            return self.get_korea_stock_data_from_naver(rowTicker, loadDays)
   
    def get_stock_list(self, limit, debug = False):
        # 한국 주식 회사 등록 정보 가지고 오기
        try:
            stockDf = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
            stockDf.종목코드 = stockDf.종목코드.map('{:06d}'.format)
            stockDf = stockDf[['회사명', '종목코드']] 
            stockDf = stockDf.rename(columns={'회사명': 'name', '종목코드': 'ticker'})
            
            # 시총 구하기
            marketCapList = []
            ranking = []
            dropIdx = []
            for idx, row in stockDf.iterrows():
                try:
                    if debug == False:
                        ticker = self.__get_ticker(row['ticker'])
                        p = web.get_quote_yahoo(ticker)['marketCap']
                        marketCap = int(p.values[0])
                        marketCapList.append(marketCap)
                    else:
                        marketCapList.append(idx)
                except:
                    dropIdx.append(idx)
                    print("[%s][%s] 시총 갖고오기 에러" % (row['name'], row['ticker']))
            
            stockDf.drop(dropIdx, inplace = True)

            rank = 1
            for i in marketCapList:
                ranking.append(rank)
                rank += 1

            stockDf['MarketCap'] = marketCapList
            stockDf = stockDf.sort_values(by='MarketCap', ascending=False)
            stockDf['ranking'] = ranking
            if limit > 0:
                stockDf = stockDf[:limit]
            return stockDf
        except:
            print("korea stock get fail")
            return None

#----------------------------------------------------------#
### 구글이 안되니 아후에서 긁자.
class TaiwanStockCrawler(StockCrawler):
    def __get_ticker(self, ticker):
        if ticker[0] == '^':
            return ticker
            
        t = ticker + ".TW"
        return t
        # try:
        #     web.get_quote_yahoo(t)['marketCap']
        #     return t
        # except:
        #     return ticker

    def get_stock_data(self, ticker, loadDays):
        rowTicker = ticker
        try:
            ticker = self.__get_ticker(ticker)
            df = super().get_stock_data(ticker, loadDays)
            return df

        except:
            return self.get_korea_stock_data_from_naver(rowTicker, loadDays)
   
class FutureCrawler(StockCrawler):            
    # 선물
    # yahoo finalnce 간략 사용법
    #https://github.com/ranaroussi/yfinance
    def get_stock_data(self, ticker, loadDays):
        future = yf.Ticker(ticker)
        if loadDays >= 1000:
            hist = future.history(period="max")  #   interval = "1m",
        else:
            hist = future.history(period="5d")  
        df = pd.DataFrame(hist)
        
        df.reset_index(inplace=True, drop=False)
        df.rename(columns={'Date': 'Date', 'High': 'high', 'Low': 'low', 'Open': 'open', 'Close': 'close', 'Volume' : 'vol'}, inplace = True)
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

        features = ['Date', 'open', 'high', 'low', 'close', 'vol']
        df = df[features]
        
        print(df)
        return df
    
    def get_stock_list(self, limit):
        with open("./list_future.txt", "r", encoding="utf-8") as f:
            targetList = f.read().splitlines()
        df = self._load_from_file(targetList)
        df['ranking'] = 0
        return df