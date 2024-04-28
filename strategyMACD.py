import os.path

import mplfinance as mpf  # mpl_finance 대신 mplfinance 사용
import matplotlib.pyplot as plt
import matplotlib as mpl

from plotly import graph_objects as go
from plotly.subplots import make_subplots
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

#https://bagal.tistory.com/263 참고
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
        if False:
            df.set_index('date', inplace=True)
            mpl.rcParams['font.family'] = 'Malgun Gothic'  # 예: 'Malgun Gothic', 'AppleGothic' 등
    
            # 별도의 패널로 MACD 관련 지표를 분리하여 표시
            apds = [
                mpf.make_addplot(ema50, color='magenta', ylabel='Price/SMA5'),
                mpf.make_addplot(ema200, color='cyan', ylabel='Price/SMA20'),
                mpf.make_addplot(macd, panel=1, color='green', ylabel='MACD'),
                mpf.make_addplot(macd_sig, panel=1, color='red'),
                mpf.make_addplot(macd_osi, type='bar', panel=2, color='purple', ylabel='Oscillator')
            ]
            # 사용자 정의 시장 색상과 스타일을 생성합니다.
            mc = mpf.make_marketcolors(up='red', down='blue', edge='inherit', wick='inherit', volume='inherit')
            s = mpf.make_mpf_style(gridstyle='-', gridcolor='grey', y_on_right=False, marketcolors=mc)

            # 패널의 높이 설정
            panel_ratios = (6, 3, 2)  # 주식 차트, MACD, Oscillator의 높이 비율을 설정합니다.
            
            # 캔들스틱 차트와 추가 지표를 함께 플롯합니다.
            mpf.plot(df, type='candle', addplot=apds, panel_ratios=panel_ratios, 
                    figratio=(20, 10),  # figratio를 사용하여 차트의 비율을 조절합니다.
                    style=s,#'charles',
                    title='{0} Stock Price'.format(sd.name_), 
                    datetime_format='%Y-%m-%d',
                    tight_layout=False, 
                    savefig=self.chart_path_)
        else:
            # 차트 데이터 준비
            date = df['date']
            open = df['open']
            high = df['high']
            low = df['low']
            close = df['close']

            # 차트 생성
            # Subplot setup (using go.Layout)
            fig = make_subplots(vertical_spacing = 0, rows=2, cols=1, row_heights=[0.7, 0.3])

            # Candlestick and EMA lines (subplot 1)
            fig.add_trace(
                go.Candlestick(x=date, open=open, high=high, low=low, close=close, name='주가',
                               increasing_line_color='red',
                                # Decreasing color for the line
                                decreasing_line_color='blue',),
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

            # Layout configuration
            fig.update_layout(
                title=sd.name_,
                xaxis_title='날짜',
                yaxis_title='가격',
                xaxis_rangeslider_visible=False
            )

            # PNG 파일로 저장
            fig.write_image(self.chart_path_)

        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, self.chart_path_))
        