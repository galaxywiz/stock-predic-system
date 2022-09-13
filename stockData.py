# talib 를 위해 아나콘다 설치 필요
# pip install .\TA_Lib-0.4.18-cp37-cp37m-win_amd64.whl        
# OR
# conda install -c quantopian ta-lib 
# conda install -c masdeseiscaracteres ta-lib
# conda install -c developer ta-lib
# OR
# pip install ta-lib
# 결국 vscode 에서 아나콘다의 파이썬으로 pip install ta-lib 하니까 됨.

from enum import Enum
import os

import talib
import talib.abstract as ta
from talib import MA_Type

import pandas as pd 
import numpy as np

import util

class BuyState (Enum):
    STAY = 0
    BUY = 1
    SELL = 2

class StockType (Enum):
    STOCK_KOREA = 0
    STOCK_USA = 1
    STOCK_TAIWAN = 2
    FUTURES = 100
    BITCOIN = 200

class StockData:
    def __init__(self, ticker, name, df):
        self.market_cap_ranking_ = 0
        self.ticker_ = ticker
        self.name_ = name
        self.chart_data_ = df

        # 구매 정보... strategy 에 전달 시킬 임시 변수
        self.buy_time_ = None
        # 매매 전략
        self.strategy_ = None
        self.strategy_action_ = BuyState.STAY
        
        # 예측 영역
        self.predic_price_ = 0        # 과거기록 누적. 이후 얼마나 잘 맞추고 있는지도 보여줌
        
        self.tele_log_ = ""
        
        self.date_time_fmt_ = "%Y-%m-%d %H:%M:%S"
        self.stock_type_ = StockType.STOCK_KOREA

    def set_strategy(self, strategy):
        self.strategy_ = strategy
    
    def get_strategy(self):
        return self.strategy_

    def set_type(self, stock_type):
        self.stock_type_ = stock_type

    def set_candle_fmt(self, fmt):
        self.date_time_fmt_ = fmt

    def get_ticker(self):
        ticker = str(self.ticker_).replace('/','_')
        return ticker

    def can_predic(self):
        size = len(self.chart_data_)
        if size < 300:
            return False
        return True

    def calc_predic_rate(self):
        if self.can_predic() == False:
            return 0
        
        now_price = self.now_price()
        rate = util.calcRate(now_price, self.predic_price_)
        return rate

    def now_price(self):
        now_candle = self.candle0()
        price = now_candle["Close"]
        return price

    def now_candle_time(self):
        now_candle = self.candle0()
        datestr = now_candle["Date"]
        return datestr

    def now_vol(self):
        now_candle = self.candle0()
        vol = now_candle["Volume"]
        return vol

    def predic_difference_rate(self):
        if self.predic_price_ == None:
            return 0
        now_price = self.now_price()
        if now_price == None:
            return 0 
        rate = util.calcRate(now_price, self.predic_price_)
        return rate
        
    # 다음 분봉 값을 예측한다
    # 이를 기반으로 매매 전략을 예측해서
    # 미리 매매 주문을 넣음
    # 예측이 실패하면 이전 주문은 바로 취소 한다
    def predic_candle(self):
        pass

    # 지금 캔들(갱신될 수 있음)
    def candle0(self):
        row_cnt = self.chart_data_.shape[0]
        if row_cnt == 0:
            return None
        return self.chart_data_.iloc[-1]

    # 완전히 완성된 캔들 (고정된 가장 최신 캔들)
    def candle1(self):
        row_cnt = self.chart_data_.shape[0]
        if row_cnt < 1:
            return None
        return self.chart_data_.iloc[-2]

    # 완성된 캔들의 직전 캔들 (지표간 cross 등 판단을 위함.)
    def candle2(self):
        row_cnt = self.chart_data_.shape[0]
        if row_cnt < 2:
            return None
        return self.chart_data_.iloc[-3]

    # 각종 보조지표, 기술지표 계산
    def calc_indicator(self):        
        arr_close = np.asarray(self.chart_data_["Close"], dtype='f8')
        arr_high = np.asarray(self.chart_data_["High"], dtype='f8')
        arr_low = np.asarray(self.chart_data_["Low"], dtype='f8')
     
        # 이평선 계산
        self.chart_data_["sma5"] = ta._ta_lib.SMA(arr_close, 5)
        self.chart_data_["sma10"] = ta._ta_lib.SMA(arr_close, 10)
        self.chart_data_["sma20"] = ta._ta_lib.SMA(arr_close, 20)
        self.chart_data_["sma50"] = ta._ta_lib.SMA(arr_close, 50)
        self.chart_data_["sma100"] = ta._ta_lib.SMA(arr_close, 100)
        self.chart_data_["sma200"] = ta._ta_lib.SMA(arr_close, 200)

        self.chart_data_["ema5"] = ta._ta_lib.EMA(arr_close, 5)
        self.chart_data_["ema10"] = ta._ta_lib.EMA(arr_close, 10)
        self.chart_data_["ema20"] = ta._ta_lib.EMA(arr_close, 20)
        self.chart_data_["ema50"] = ta._ta_lib.EMA(arr_close, 50)
        self.chart_data_["ema100"] = ta._ta_lib.EMA(arr_close, 100)
        self.chart_data_["ema200"] = ta._ta_lib.EMA(arr_close, 200)

        self.chart_data_["wma5"] = ta._ta_lib.WMA(arr_close, 5)
        self.chart_data_["wma10"] = ta._ta_lib.WMA(arr_close, 10)
        self.chart_data_["wma20"] = ta._ta_lib.WMA(arr_close, 20)
        self.chart_data_["wma50"] = ta._ta_lib.WMA(arr_close, 50)
        self.chart_data_["wma100"] = ta._ta_lib.WMA(arr_close, 100)
        self.chart_data_["wma200"] = ta._ta_lib.WMA(arr_close, 200)

        macd, signal, osi = ta._ta_lib.MACD(arr_close, fastperiod=12, slowperiod=26, signalperiod=9)
        self.chart_data_["MACD"] = macd
        self.chart_data_["MACDSignal"] = signal
        self.chart_data_["MACDOsi"] = osi
  
        #볼린저 계산
        upper, middle, low = ta._ta_lib.BBANDS(arr_close, 20, 2, 2, matype=MA_Type.SMA)
        self.chart_data_["bbandUp"] = upper
        self.chart_data_["bbandMid"] = middle
        self.chart_data_["bbandLow"] = low

        # 기타 자주 사용되는 것들
        self.chart_data_["rsi"] = ta._ta_lib.RSI(arr_close, 14)
        self.chart_data_["cci"] = ta._ta_lib.CCI(arr_high, arr_low, arr_close, 14)
        self.chart_data_["williumR"] = ta._ta_lib.WILLR(arr_high, arr_low, arr_close, 14)
        self.chart_data_["parabol"] = ta._ta_lib.VAR(arr_close, 5, 1)
        self.chart_data_["adx"]  = ta._ta_lib.ADX(arr_high, arr_low, arr_close, 14)
        self.chart_data_["plusDI"]  = ta._ta_lib.PLUS_DI(arr_high, arr_low, arr_close, 14)
        self.chart_data_["plusDM"]  = ta._ta_lib.PLUS_DM(arr_high, arr_low, 14)
       
        self.chart_data_["atr"] = ta._ta_lib.ATR(arr_high, arr_low, arr_close, 14)
        