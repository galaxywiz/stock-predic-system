import os.path

import pandas as pd
import numpy as np

import mplfinance as mpf  # mpl_finance 대신 mplfinance 사용
import matplotlib.pyplot as plt
import matplotlib as mpl

import talib.abstract as ta
from talib import MA_Type

from stockStrategy import StockStrategy

class BollengerStockStrategy(StockStrategy):
    def make_indicators(self, start = 0, end = 0):
        df_copy = super().make_indicators(start, end)
        if df_copy is None:
            return None
        df = df_copy.copy()

        window = 20 # 이동평균선과 표준편차 계산을 위한 윈도우 크기
        multiplier = 2 # 표준편차의 배수
    
        # 종가 기준으로 볼린저 밴드 계산
        arr_close = np.asarray(df['close'], dtype='f8')
        upper, middle, low = ta._ta_lib.BBANDS(arr_close, window, multiplier, 2, matype=MA_Type.SMA)
        df["Upper"] = upper
        df["Middle"] = middle
        df["Lower"] = low
        return df
    
    def bid_price(self, candle):
        close = candle['close']
        lower = candle['Lower']
        if close <= lower:
            return True
        return False
    
    def ask_price(self, candle):
        close = candle['close']
        upper = candle['Upper']
        if close >= upper:
            return True
        return False

    def print_chart(self):
        sd = self.stock_data_
        
        # 이미지 저장
        dir = self.char_dir_ + "/bol"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.chart_path_ = "%s/%s.png" % (dir, sd.name_)

        chart_len = len(sd.chart_data_)
        c_len = self.chart_len_
        df = self.make_indicators(start=chart_len - c_len * 2, end=chart_len)
        df = df[-c_len:]
        
        # ------------- 차트 그리기 ---------------- #        
        df.set_index('date', inplace=True)
        
        mpl.rcParams['font.family'] = 'Malgun Gothic'  # 예: 'Malgun Gothic', 'AppleGothic' 등
        # 볼린저  밴드를 추가 지표로 설정
        add_plot = [
            mpf.make_addplot(df['Upper'], color='red', ylabel='Upper'),
            mpf.make_addplot(df['Middle'], color='black', ylabel='Middle'),
            mpf.make_addplot(df['Lower'], color='blue', ylabel='Lower')
        ]
        
        # 캔들스틱 차트와 볼린저 밴드 플롯
        mpf.plot(df, type='candle', addplot=add_plot, 
                figratio=(20, 10),  # figratio를 사용하여 차트의 비율을 조절합니다.
                style='charles',
                title='{0} Stock Price'.format(sd.name_), 
                datetime_format='%Y-%m-%d',
                savefig=self.chart_path_)

        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, self.chart_path_))
        