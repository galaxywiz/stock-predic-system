import os.path
import matplotlib.pyplot as plt
import stockData
import talib.abstract as ta
from talib import MA_Type
from sklearn import linear_model
import numpy as np
from stockStrategy import StockStrategy

class BollengerStockStrategy(StockStrategy):
    def make_indicators(self, idx = 0):
        df_copy = super().make_indicators(idx)
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
        df = self.make_indicators()
        plt.close()
        # 한글 폰트 설정
        plt.rc('font', family='Malgun Gothic')   # 나눔 폰트를 사용하려면 해당 폰트 이름을 지정
        plt.figure(figsize=(16, 8))

        for i in ['close', 'Upper', 'Middle', 'Lower']:
            plt.plot(df['date'], df[i], label=i)

        plt.xlabel('date')
        plt.ylabel("Price")
        title = "%s(%s)" % (sd.name_, sd.ticker_)
        plt.title(title)

        # 범례 추가
        plt.legend()

        # 이미지 저장
        dir = self.char_dir_ + "/bol"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.chart_path_ = "%s/%s.png" % (dir, sd.name_)
        plt.savefig(self.chart_path_)
        plt.close()
      
        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, self.chart_path_))
        