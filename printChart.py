import pandas as pd

import datetime

import plotly.graph_objects as go
import logger
import traceback

import util as u
import os
from stockData import StockData

font_title = {'family': 'D2Coding', 'size': 24, 'color': 'black'}

class PrintChart:
    #----------------------------------------------------------#
    # 그래프 그리기
    def saveFigure(dir, sd, date_fmt):
        try:
            color_up = "Green"
            color_down = "Red"
            data_len = 50

            candle = sd.candle0()
            close_price = candle['close']
            per_close = close_price / 100
            dateT = candle['date'] + datetime.timedelta(days=1)
            #dateT = datetime.datetime.strptime(candle['date'], date_fmt).date() + datetime.timedelta(days=1)
            predic = sd.predic_price_[0]

            open_price = predic - per_close
            color_predic = color_up
            arrow = 'arrow-up'
            if close_price > predic:
                color_predic = color_down
                arrow = 'arrow-down'
                open_price = predic + per_close

            group = ['date','open','high','low','close']
            df = sd.chart_data_[group].copy()
            df = df.tail(data_len)
            pdf = pd.DataFrame(data=[[dateT, open_price, predic + (per_close*2) , predic - (per_close*2), predic]], 
                            columns=group)
            df = pd.concat([df, pdf], ignore_index=True)
            fig = go.Figure(data=[go.Candlestick(x=df['date'],
                                    open=df['open'],
                                    high=df['high'],
                                    low=df['low'],
                                    close=df['close'],
                                    increasing_line_color= color_up,
                                    decreasing_line_color= color_down, 
                                    name='day data')])

            fig.add_trace(
                go.Scatter(
                    mode='markers',
                    x = [dateT] ,
                    y = [predic],
                    marker_symbol=arrow,
                    marker=dict(
                        color=color_predic,
                        size=20
                    ),
                    name = ('예측')
                )
            )
            fig.layout = dict(title=sd.name_, 
                              xaxis = dict(type="category",
                                         categoryorder='category ascending',
                                         ))

            fig.update_xaxes(nticks=5)     

            val = u.calcRate(close_price, predic)
            title = "%s의 [%s] 예측 종가 [%2.2f] 전일대비[%2.2f]" % (sd.name_, dateT.strftime(date_fmt), predic, val*100) 
            fig.update_layout(xaxis_title='date',
                            yaxis_title="Close price",
                            title_text=title,
                            xaxis={"rangeslider":{"visible":False}}
                            )
            if not os.path.exists(dir):
                os.makedirs(dir)
            
            file_name = "flg_%s.png" % (sd.name_)
            file_path = "%s/%s" % (dir, file_name)
            if os.path.isfile(file_path) == True:
                os.remove(file_path)
            
            fig.write_image(file_path)
            del fig
            
            print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, file_name))
            return file_path

        except:
            print("$ 차트 갱신 실패 [%s]" % (sd.name_))
            logger.error(traceback.format_exc())