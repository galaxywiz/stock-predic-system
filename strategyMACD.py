import os.path
import matplotlib.pyplot as plt
import stockData
import talib.abstract as ta
from talib import MA_Type
from sklearn import linear_model
import numpy as np
from stockStrategy import StockStrategy

class MacdStockStrategy(StockStrategy):
    def make_indicators(self, idx = 0):
        df_copy = super().make_indicators(idx)
        if df_copy is None:
            return None
        df = df_copy.copy()

        # 종가 기준으로 볼린저 밴드 계산
        arr_close = np.asarray(df["Close"], dtype='f8')
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

    def print_chart(self):
        sd = self.stock_data_
        df = self.make_indicators()
        plt.close()
        # 한글 폰트 설정
        plt.rc('font', family='Malgun Gothic')   # 나눔 폰트를 사용하려면 해당 폰트 이름을 지정
        plt.figure(figsize=(16, 8))

        for i in ['Close', 'MACD', 'MACDSignal']:
            plt.plot(df['Date'], df[i], label=i)

        plt.xlabel("Date")
        plt.ylabel("Price")
        title = "%s(%s)" % (sd.name_, sd.ticker_)
        plt.title(title)

        # 범례 추가
        plt.legend()

        # 이미지 저장
        dir = self.char_dir_ + "/macd"
        if not os.path.exists(dir):
            os.makedirs(dir)
        save_file = "%s/%s.png" % (dir, sd.name_)
        plt.savefig(save_file)
        plt.close()
      
        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, save_file))
        