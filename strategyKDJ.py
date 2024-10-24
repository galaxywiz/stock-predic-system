import os.path

import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib as mpl

from plotly import graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

import talib.abstract as ta
import pandas as pd
import numpy as np
from stockStrategy import StockStrategy

class KdjStockStrategy(StockStrategy):
    def make_indicators(self, start=0, end=0):
        df_copy = super().make_indicators(start, end)
        if df_copy is None:
            return None
        df = df_copy.copy()

        # 종가 기준으로 KDJ 지표 계산
        arr_high = np.asarray(df['high'], dtype='f8')
        arr_low = np.asarray(df['low'], dtype='f8')
        arr_close = np.asarray(df['close'], dtype='f8')
        
        # K, D 계산 (Talib의 Stochastic Oscillator를 사용)
        slowk, slowd = ta.STOCH(arr_high, arr_low, arr_close, 
                                fastk_period=9, slowk_period=3, slowk_matype=0, 
                                slowd_period=3, slowd_matype=0)
        
        # J 계산 (3K - 2D)
        j = 3 * slowk - 2 * slowd
        
        df['K'] = slowk
        df['D'] = slowd
        df['J'] = j
        return df

    def bid_price(self, candle):
        k = candle['K']
        d = candle['D']
        if k > d:
            return True
        return False

    def ask_price(self, candle):
        k = candle['K']
        d = candle['D']
        if k < d:
            return True
        return False

    def print_chart(self):
        sd = self.stock_data_

        # 이미지 저장 파일
        dir = self.char_dir_ + "/kdj"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.chart_path_ = "%s/%s.png" % (dir, sd.name_)

        chart_len = len(sd.chart_data_)
        c_len = self.chart_len_
        df = self.make_indicators(start=chart_len - c_len * 2, end=chart_len)
        df = df[-c_len:]

        ema50 = df['ema50']
        ema200 = df['ema200']
        k = df['K']
        d = df['D']
        j = df['J']

        # ------------- 차트 그리기 ---------------- #
        # 차트 데이터 준비
        date = df['date']
        open = df['open']
        high = df['high']
        low = df['low']
        close = df['close']

        # 차트 생성
        fig = make_subplots(
            vertical_spacing=0.03,
            rows=2, cols=1,
            subplot_titles=("주식일봉차트", "KDJ"),
            row_heights=[0.7, 0.3],
            shared_xaxes=True,
        )

        # Candlestick and EMA lines (subplot 1)
        fig.add_trace(
            go.Candlestick(x=date, open=open, high=high, low=low, close=close, name='주가'),
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

        # KDJ lines (subplot 2)
        fig.add_trace(
            go.Scatter(x=date, y=k, line=dict(color='red', width=1), name='K'),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=date, y=d, line=dict(color='blue', width=1), name='D'),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=date, y=j, line=dict(color='green', width=2), name='J'),
            row=2, col=1
        )

        now_price = sd.now_price()
        now_time = sd.now_candle_time()
        date_str = now_time.strftime("%Y-%m-%d")
        title = "{0}[{1}], {2}일 종가:{3:,.2f}$".format(sd.name_, sd.ticker_, date_str, now_price)
        
        # KDJ의 Y축 범위 설정 (0~100)
        fig.update_yaxes(range=[-150, 150], row=2, col=1)

        # Layout configuration
        fig.update_layout(
            title=title,
            yaxis_title='가격',
            xaxis_rangeslider_visible=False,
            template='ggplot2',
        )

   #     fig.show()
        # PNG 파일로 저장
        fig.write_image(self.chart_path_)

        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, self.chart_path_))
