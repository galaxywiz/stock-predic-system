import os.path

import mplfinance as mpf  # mpl_finance 대신 mplfinance 사용
import matplotlib.pyplot as plt
import matplotlib as mpl

#plotly 설명
#https://wikidocs.net/book/8909
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

import talib.abstract as ta
from talib import MA_Type

import pandas as pd
import numpy as np
from stockStrategy import StockStrategy

class MacdStockStrategy(StockStrategy):
    def make_indicators(self, start = 0, end = 0):
        df_copy = super().make_indicators(start, end)
        if df_copy is None:
            return None
        df = df_copy.copy()

        # 종가 기준으로 볼린저 밴드 계산
        arr_close = np.asarray(df['close'], dtype='f8')
        macd, signal, osi = ta._ta_lib.MACD(arr_close, fastperiod=12, slowperiod=26, signalperiod=9)
        df["MACD"] = macd
        df["MACDSignal"] = signal
        df["MACDOsi"] = osi
        return df
    
    def bid_price(self, candle):
        macd = candle['MACD']
        signal = candle['MACDSignal']
        if macd > signal:
            return True
        return False
    
    def ask_price(self, candle):
        macd = candle['MACD']
        signal = candle['MACDSignal']
        if macd < signal:
            return True
        return False

# https://bagal.tistory.com/263 참고
# https://junpyopark.github.io/MACD_Plotting/
    def print_chart(self):
        sd = self.stock_data_
        
        # 이미지 저장 파일
        dir = self.char_dir_ + "/macd"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.chart_path_ = "%s/%s.png" % (dir, sd.name_)

        chart_len = len(sd.chart_data_)
        c_len = self.chart_len_
        df = self.make_indicators(start=chart_len - c_len * 2, end=chart_len)
        df = df[-c_len:]

        ema50 = df['ema50']
        ema200 = df['ema200']
        macd = df['MACD']
        macd_sig = df['MACDSignal']
        macd_osi = df['MACDOsi']
        
        # ------------- 차트 그리기 ---------------- #
        # 차트 데이터 준비
        date = df['date']
        open = df['open']
        high = df['high']
        low = df['low']
        close = df['close']

        # 차트 생성
        # Subplot setup (using go.Layout)
        fig = make_subplots(
             vertical_spacing = 0.03,
             rows=2, cols=1,
             subplot_titles=("주식일봉차트", "MACD",),
             row_heights=[0.7, 0.3],
             shared_xaxes=True,
            )

        # Candlestick and EMA lines (subplot 1)
        fig.add_trace(
            go.Candlestick(x=date, open=open, high=high, low=low, close=close, name='주가',
                           #increasing_line_color='red',                                
                           #decreasing_line_color='blue',
                           ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=date, y=ema50, line=dict(color='red', width=1), name="ema50"),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=date, y=ema200, line=dict(color='blue', width=1), name="ema200"),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=date, y=macd, line=dict(color='red', width=1), name='MACD'),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=date, y=macd_sig, line=dict(color='blue', width=1), name='Signal Line'),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=date, y=macd_osi, name='MACD Hist'),
            row=2, col=1
        )

        now_price = sd.now_price()
        now_time = sd.now_candle_time()
        date_str = now_time.strftime("%Y-%m-%d")
        title = "{0}[{1}], {2}일 종가:{3:,.2f}$".format(sd.name_, sd.ticker_, date_str, now_price)
       
        # Layout configuration
        fig.update_layout(
            title=title,
            yaxis_title='가격',
            xaxis_rangeslider_visible=False,
            template='ggplot2',
        )

        # PNG 파일로 저장
        fig.write_image(self.chart_path_)

        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, self.chart_path_))
        