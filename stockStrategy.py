import pandas as pd
#import matplotlib.pyplot as plt
import stockData


import numpy as np
import plotly.graph_objects as go
import time

class StockStrategy:
    def __init__(self, sd):
        self.stock_data_ = sd

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
        df = sd.chart_data_.tail(220)
        
        

        fig = go.Figure()
        for i in ['Close','priceTL','TL-2SD', 'TL-SD',
            'TL+SD', 'TL+2SD']:
            fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df[i],
                name=i
            ))

        fig.update_layout(
        xaxis_title="x Axis Title",
            yaxis_title="y Axis Title",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="#7f7f7f"
            ),
            title={'text': "Plot Title",'xanchor': 'center','y':0.995,
                'x':0.5,
                'yanchor': 'top'},
        )
        print("$ 차트 준비 [%s]" % (sd.name_))
        # 그래프 준비
        fig.show()

        save_file = "chart/%s.png" % sd.name_
        fig.write_image(save_file)
        del fig
            
        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, save_file))
        