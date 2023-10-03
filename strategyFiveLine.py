import os.path
import matplotlib.pyplot as plt
import stockData
import talib.abstract as ta
from talib import MA_Type
from sklearn import linear_model
import numpy as np
from stockStrategy import StockStrategy

class FiveLineStockStrategy(StockStrategy):
    def make_indicators(self, idx = 0):
        df_copy = super().make_indicators(idx)
        if df_copy is None:
            return None
        df = df_copy.copy()

        reg = linear_model.LinearRegression()
        df.loc[:, 'itx'] =[i for i in range(1,len(list(df['Close'])) + 1)]
        # x , y
        reg.fit (df['itx'].values.reshape(-1, 1),df['Close'])
        df.loc[:, 'coef'] = reg.coef_[0]
        df.loc[:, 'intercept'] = reg.intercept_
        # y = c+x*b = 截距+x*斜率
        #추세선
        df.loc[:, 'priceTL'] = df['intercept'] + (df['itx'] * df['coef'])
        # 오차
        df.loc[:, 'y-TL'] = df['Close'] - df['priceTL']
        # 표준편차
        df.loc[:, 'SD'] = df['y-TL'].std()
        
        #매우 낙관적인 선: 추세선은 위의 2 표준편차이며, 추가 상승 확률은 2.2%입니다(아래 그림의 노란색 선).
        #낙관선: 추세선 위 1 표준편차, 추가 상승 확률 15.8%(아래 그림의 연한 파란색 선)
        #추세선: 일정 기간 동안의 평균 가격을 연결하는 직선(아래 그림의 분홍색 선).
        #비관적 선: 추세선은 1 표준편차 이하이며, 추가 하락 확률은 15.8%(아래 그림의 진한 파란색 선)입니다.
        #극도로 비관적인 선 : 추세선은 아래 2표준편차이고, 추가 하락 확률은 2.2%이다(아래 그림 녹색선).        
        df.loc[:, 'TL-2SD'] = df['priceTL'] - (2 * df['SD'])
        df.loc[:, 'TL-SD'] = df['priceTL'] - (1 * df['SD'])
        df.loc[:, 'TL+SD'] = df['priceTL'] + (1 * df['SD'])
        df.loc[:, 'TL+2SD'] = df['priceTL'] + (2 * df['SD'])
        return df
    
    def bid_price(self, candle):
        close = candle['Close']
        TL2SD = candle['TL-2SD']
        if close <= TL2SD:
            return True
        return False
    
    def ask_price(self, candle):
        close = candle['Close']
        TL2SD = candle['TL+2SD']
        if close >= TL2SD:
            return True
        return False
    
    def print_chart(self):
        sd = self.stock_data_
        df = self.make_indicators()
        plt.close()
        # 한글 폰트 설정
        plt.rc('font', family='Malgun Gothic')   # 나눔 폰트를 사용하려면 해당 폰트 이름을 지정
        plt.figure(figsize=(16, 8))

        for i in ['Close', 'priceTL', 'TL-2SD', 'TL-SD', 'TL+SD', 'TL+2SD']:
            plt.plot(df['Date'], df[i], label=i)

        plt.xlabel("Date")
        plt.ylabel("Price")
        title = "%s(%s)" % (sd.name_, sd.ticker_)
        plt.title(title)

        # 범례 추가
        plt.legend()

        # 이미지 저장
        dir = self.char_dir_ + "/five"
        if not os.path.exists(dir):
            os.makedirs(dir)
        save_file = "%s/%s.png" % (dir, sd.name_)
        plt.savefig(save_file)
        plt.close()
      
        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, save_file))
        