import os.path
import pandas as pd
import matplotlib.pyplot as plt
import stockData


import numpy as np
import plotly.graph_objects as go
import plotly.io
import time


class StockStrategy:
    def __init__(self, stock_data, char_dir):
        self.stock_data_ = stock_data
        self.char_dir_ = char_dir

    # 매수 가격인가?
    def bid_price(self):
        pass

    # 매도 가격인가?
    def ask_price(self):
        pass
    
    # 차트 출력해서 맞는지 검증
    def print_chart(self):
        pass

class FiveLineStockStrategy(StockStrategy):
    def bid_price(self):
        
        return super().bid_price()
    
    def ask_price(self):

        return super().ask_price()
    
    def print_chart(self):
        sd = self.stock_data_
        # 데이터 프레임을 최근 120일로 슬라이싱합니다.
        df = sd.chart_data_ #.tail(120)               
        
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
        dir = self.char_dir_
        if not os.path.exists(dir):
            os.makedirs(dir)
        save_file = "%s/%s.png" % (dir, sd.name_)
        plt.savefig(save_file)
        plt.close()

        # 그래프 표시
        #plt.show()

        # fig = go.Figure()
        # for i in ['Close','priceTL','TL-2SD', 'TL-SD',
        #     'TL+SD', 'TL+2SD']:
        #     fig.add_trace(
        #     go.Scatter(
        #         x=df['Date'],
        #         y=df[i],
        #         name=i
        #     ))

        # fig.update_layout(
        # xaxis_title="x Axis Title",
        #     yaxis_title="y Axis Title",
        #     font=dict(
        #         family="Courier New, monospace",
        #         size=18,
        #         color="#7f7f7f"
        #     ),
        #     title={'text': "Plot Title",'xanchor': 'center','y':0.995,
        #         'x':0.5,
        #         'yanchor': 'top'},
        # )
        # print("$ 차트 준비 [%s]" % (sd.name_))
        # # 그래프 준비
        # time.sleep(0.1)

        # save_file = "./chart/%s.png" % sd.name_
        # fig.write_image(save_file)
        # ##, format="png", plotlyjs="https://cdn.plot.ly/plotly-latest.min.js")
        # del fig
            
        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, save_file))
        