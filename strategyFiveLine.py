import os.path

import pandas as pd
import numpy as np

import mplfinance as mpf  # mpl_finance 대신 mplfinance 사용
import matplotlib.pyplot as plt

import talib.abstract as ta
from talib import MA_Type

from sklearn import linear_model
from stockStrategy import StockStrategy

class FiveLineStockStrategy(StockStrategy):
    able_back_test_ = False
    def make_indicators(self, start = 0, end = 0):
        df_copy = super().make_indicators(start, end)
        if df_copy is None:
            return None
        df = df_copy.copy()

        reg = linear_model.LinearRegression()
        df.loc[:, 'itx'] =[i for i in range(1,len(list(df['close'])) + 1)]
        # x , y
        reg.fit (df['itx'].values.reshape(-1, 1),df['close'])
        df.loc[:, 'coef'] = reg.coef_[0]
        df.loc[:, 'intercept'] = reg.intercept_
        # y = c+x*b = 截距+x*斜率
        #추세선
        df.loc[:, 'priceTL'] = df['intercept'] + (df['itx'] * df['coef'])
        # 오차
        df.loc[:, 'y-TL'] = df['close'] - df['priceTL']
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
        close = candle['close']
        TL2SD = candle['TL-2SD']
        if close <= TL2SD:
            return True
        return False
    
    def ask_price(self, candle):
        close = candle['close']
        TL2SD = candle['TL+2SD']
        if close >= TL2SD:
            return True
        return False
    
    def print_chart(self):
        sd = self.stock_data_
        
        # 이미지 저장
        dir = self.char_dir_ + "/five"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.chart_path_ = "%s/%s.png" % (dir, sd.name_)

        chart_len = len(sd.chart_data_)
        c_len = self.chart_len_
        df = self.make_indicators(start=chart_len - c_len * 2, end=chart_len)
        df = df[-c_len:]

        # ------------- 차트 그리기 ---------------- #
        plt.rc('font', family='Malgun Gothic')

        df.set_index('date', inplace=True)
        add_plot = []

        for i in ['priceTL', 'TL-2SD', 'TL-SD', 'TL+SD', 'TL+2SD']:
            add_plot.append(mpf.make_addplot(df[i], ylabel=i))

        # 캔들스틱 차트와 볼린저 밴드 플롯
        mpf.plot(df, type='candle', addplot=add_plot, 
                figratio=(20, 10),  # figratio를 사용하여 차트의 비율을 조절합니다.
                style='charles',
                title='{0} Stock Price'.format(sd.name_), 
                datetime_format='%Y-%m-%d',
                savefig=self.chart_path_)
        
        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, self.chart_path_))
        