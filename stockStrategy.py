import matplotlib.pyplot as plt
import stockData
import talib.abstract as ta
from talib import MA_Type
from tradingStatment import Transaction, TradingStatement

class StockStrategy:
    def __init__(self, stock_data, char_dir):
        self.stock_data_ = stock_data
        self.char_dir_ = char_dir

    # 전략 만들기
    def make_indicators(self, idx):
        pass

    # 매수 가격인가?
    def bid_price(self, candle):
        pass

    # 매도 가격인가?
    def ask_price(self, candle):
        pass
    
    def back_test(self, balance = 0):
        df = self.stock_data_.chart_data_
        tranding_statement = TradingStatement(self.stock_data_)
        transaction = Transaction()
        
        state = stockData.TradingState.BUY
        lenth = len(df)
        # data 는 1년 후 (working 220일) 지표가 정상적으로 로딩 된다다
        for idx in range(220, lenth, 1):
            df = self.make_indicators(idx)
            if df is None:
                break
            candle = df.iloc[-1]
            
            if state == stockData.TradingState.BUY:
                if self.bid_price(candle):
                    state = stockData.TradingState.SELL
                    transaction.set_bid(candle)

            elif state == stockData.TradingState.SELL:
                if self.ask_price(candle):
                    state = stockData.TradingState.BUY
                    transaction.set_ask(candle)
                    tranding_statement.add_transaction(transaction)

                    transaction = Transaction()
                    
        tranding_statement.log()
        return tranding_statement
        

    # 차트 출력해서 맞는지 검증
    def print_chart(self):
        pass

