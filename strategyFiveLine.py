### https://invest.wessiorfinance.com/notation.html
##樂活五線譜
import os.path

import pandas as pd
import numpy as np

import mplfinance as mpf  # mpl_finance 대신 mplfinance 사용
import matplotlib.pyplot as plt
import matplotlib as mpl
from plotly import graph_objects as go

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
        if False:
            df.set_index('date', inplace=True)
            mpl.rcParams['font.family'] = 'Malgun Gothic'  # 예: 'Malgun Gothic', 'AppleGothic' 등

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
        else:
            # 차트 데이터 준비
            date = df['date']
            open = df['open']
            high = df['high']
            low = df['low']
            close = df['close']

            price_tl = df['priceTL']
            tl_m2sd = df['TL-2SD']
            tl_msd = df['TL-SD']
            tl_psd = df['TL+SD']
            tl_p2sd = df['TL+2SD']

            # 이동평균선 돌파 전략에서 사용하는 단기일과 장기일의 설정은 투자자의 투자 스타일, 분석 대상 시장, 시장 상황 등에 따라 다양하게 조정될 수 있습니다.

            # 일반적인 기준:

            # 단기 이동평균선: 5일, 10일, 20일선 등 단기적인 가격 변동 추세를 반영합니다. 빠르게 변화하는 시장 상황을 파악하는 데 유용하며, 주로 매매 신호를 확인하는 데 사용됩니다.
            # 장기 이동평균선: 20일, 50일, 100일, 200일선 등 장기적인 가격 변동 추세를 반영합니다. 시장의 기본적인 방향성을 파악하는 데 유용하며, 트렌드 확인 및 지지/저항 수준 설정에 활용됩니다.
            # 다음은 몇 가지 예시입니다:

            # 공격적인 투자: 5일 단기 이동평균선과 20일 장기 이동평균선 돌파 전략을 사용하여 단기적인 매매 기회를 적극적으로 포착합니다.
            # 보수적인 투자: 20일 단기 이동평균선과 50일 장기 이동평균선 돌파 전략을 사용하여 장기적인 추세 확인 후 투자 결정을 내립니다.
            # 트렌드 추종: 50일 단기 이동평균선과 200일 장기 이동평균선 돌파 전략을 사용하여 강력한 트렌드 확인 후 장기적인 투자를 진행합니다.
            ema5 = df['ema5']
            ema20 = df['ema20']
            # 차트 생성
            fig = go.Figure(
                data=[
                    go.Candlestick(x=date, open=open, high=high, low=low, close=close,
                                   # Increasing color for the line
                                   increasing_line_color='red',
                                   # Decreasing color for the line
                                   decreasing_line_color='blue',
                                   name = '주가'
                                  ),
                    
                    go.Scatter(x=date, y=tl_p2sd, line=dict(width=1), name="매우 낙관선"),
                    go.Scatter(x=date, y=tl_psd, line=dict(width=1), name="낙관선"),
                    go.Scatter(x=date, y=price_tl, line=dict(width=1), name="추세선"),
                    go.Scatter(x=date, y=tl_msd, line=dict(width=1), name="비관선"),
                    go.Scatter(x=date, y=tl_m2sd, line=dict(width=1), name="매우 비관선"),

                    go.Scatter(x=date, y=ema5, line=dict(color='red', width=1), name="ema5"),
                    go.Scatter(x=date, y=ema20, line=dict(color='blue', width=1), name="ema20"),                    
                ]
            )
            fig.update_layout(
                title=sd.name_,
                xaxis_title='날짜', 
                yaxis_title='가격',
                xaxis_rangeslider_visible=False
                )

            # PNG 파일로 저장
            fig.write_image(self.chart_path_)

        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, self.chart_path_))
        