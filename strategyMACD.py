import os.path
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib import font_manager, rc

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
    def print_chart(self):
        sd = self.stock_data_
        chart_len = len(sd.chart_data_)
        df = self.make_indicators(start= chart_len - 100, end= chart_len)

        plt.close()
        # 한글 폰트 설정
        plt.rc('font', family='Malgun Gothic')   # 나눔 폰트를 사용하려면 해당 폰트 이름을 지정
        plt.figure(figsize=(16, 8))
        spec = gridspec.GridSpec(ncols=1, nrows=2)
        
        #종가 그리기
        plt.subplot(spec[0])
        plt.plot(df['date'], df['close'], label='close')
        plt.legend()

        #macd
        plt.subplot(spec[1])
        for i in ['MACD', 'MACDSignal']:
            plt.plot(df['date'], df[i], label=i)
        
        title = "%s(%s)" % (sd.name_, sd.ticker_)
        plt.title(title)

        # 범례 추가
        plt.legend()

        # 이미지 저장
        dir = self.char_dir_ + "/macd"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.chart_path_ = "%s/%s.png" % (dir, sd.name_)
        plt.savefig(self.chart_path_)
        plt.close()
      
        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, self.chart_path_))
        