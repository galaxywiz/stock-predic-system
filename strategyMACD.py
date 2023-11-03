import os.path

from matplotlib import gridspec
from matplotlib import font_manager, rc

from mpl_finance import candlestick2_ohlc
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import stockData
import talib.abstract as ta
from talib import MA_Type
from sklearn import linear_model
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
        chart_len = len(sd.chart_data_)
        df = self.make_indicators(start= chart_len - 100, end= chart_len)

        # 차트 레이아웃을 설정합니다.
        fig = plt.figure(figsize=(12,10))
        ax_main = plt.subplot2grid((5, 1), (0, 0), rowspan=3)
        ax_sub = plt.subplot2grid((5, 1), (3, 0))
        ax_sub2 = plt.subplot2grid((5, 1), (4, 0))

        index = df.index.astype('str')
        # 메인차트를 그립니다.
        ax_main.set_title('{0} Stock Price'.format(sd.name_),fontsize=20)
        ax_main.plot(index, df['sma5'], label='MA5')
        ax_main.plot(index, df['sma20'], label='MA20')
        candlestick2_ohlc(ax_main, df['open'],df['high'],
                        df['low'],df['close'],width=0.6)

        ax_main.legend(loc=5)

        # 아래는 날짜 인덱싱을 위한 함수 입니다.
        def mydate(x, pos):
            try:
                pos = int(round(x))
                if 0 <= pos < len(index):
                    return index[pos]
                else:
                    return ''
            except ValueError:
                return ''

        # ax_sub 에 MACD 지표를 출력합니다.
        ax_sub.set_title('MACD',fontsize=15)
        df['MACD'].iloc[0] = 0
        ax_sub.plot(index,df['MACD'], label='MACD')
        ax_sub.plot(index,df['MACDSignal'], label='MACD Signal')
        ax_sub.legend(loc=2)

        # ax_sub2 에 MACD 오실레이터를 bar 차트로 출력합니다.
        ax_sub2.set_title('MACD Oscillator',fontsize=15)
        oscillator = df['MACDOsi']
        oscillator.iloc[0] = 1e-16
        ax_sub2.bar(list(index),list(oscillator.where(oscillator > 0)), 0.7)
        ax_sub2.bar(list(index),list(oscillator.where(oscillator < 0)), 0.7)

        # x 축을 조정합니다.
        ax_main.xaxis.set_major_locator(ticker.MaxNLocator(7))
        ax_main.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
        ax_sub.xaxis.set_major_locator(ticker.MaxNLocator(7))
        ax_sub2.xaxis.set_major_locator(ticker.MaxNLocator(7))
        fig.autofmt_xdate()

        # 차트끼리 충돌을 방지합니다.
        plt.tight_layout()
      #  plt.show()

        # 이미지 저장
        dir = self.char_dir_ + "/macd"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.chart_path_ = "%s/%s.png" % (dir, sd.name_)
        plt.savefig(self.chart_path_)
        plt.close()
      
        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, self.chart_path_))
        