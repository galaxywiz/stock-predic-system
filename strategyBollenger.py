import os.path

import pandas as pd
import numpy as np

import mplfinance as mpf  # mpl_finance 대신 mplfinance 사용
import matplotlib.pyplot as plt
import matplotlib as mpl

from plotly import graph_objects as go

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
        upper = df['Upper']
        middle = df['Middle']
        lower = df['Lower']

            # 차트 데이터 준비
        date = df['date']
        open = df['open']
        high = df['high']
        low = df['low']
        close = df['close']

        # 차트 생성
        fig = go.Figure(
            data=[
                go.Candlestick(x=date, open=open, high=high, low=low, close=close,
                               # Increasing color for the line
                            #    increasing_line_color='red',
                            #    # Decreasing color for the line
                            #    decreasing_line_color='blue',
                               name = '주가'
                              ),
                go.Scatter(x=date, y=upper, line=dict(color='red', width=1), name="상단 밴드"),
                go.Scatter(x=date, y=middle, line=dict(color='gray', width=1), name="중간선"),
                go.Scatter(x=date, y=lower, line=dict(color='blue', width=1), name="하단 밴드"),
            ]
        )
        now_price = sd.now_price()
        now_time = sd.now_candle_time()
        date_str = now_time.strftime("%Y-%m-%d")
        title = "{0}[{1}], {2}일 종가:{3:,.2f}$".format(sd.name_, sd.ticker_, date_str, now_price)
        fig.update_layout(
            title=title,
            xaxis_title='날짜', 
            yaxis_title='가격',
            xaxis_rangeslider_visible=False,
            template='ggplot2',
            )

        # PNG 파일로 저장
        fig.write_image(self.chart_path_)

        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, self.chart_path_))
        