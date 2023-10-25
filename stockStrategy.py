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
        sd = self.stock_data_
        lenth = len(sd.chart_data_)
        if idx > 0:
            if lenth < idx:
                return None
            df = sd.chart_data_[:idx]  
        else:
            df = sd.chart_data_
        return df

    # 매수 가격인가?
    def bid_price(self, candle):
        pass

    # 매도 가격인가?
    def ask_price(self, candle):
        pass
    
    # kelly_rate 를 매 순간 마다 계산 해 보는게 좋을듯...
    def back_test(self, transaction_simul=True, balance=0, kelly_rate=0):
        df = self.stock_data_.chart_data_
        trading_statement = TradingStatement(sd=self.stock_data_
                                             , trading=self
                                             , balance=balance
                                             , kelly_rate=kelly_rate)
        transaction = Transaction()
        
        state = stockData.TradingState.BUY
        length = len(df)
        # data 는 1년 후 (working 220일) 지표가 정상적으로 로딩 된다
        WORKING_DAY_PER_YEAR = 220
        for idx in range(WORKING_DAY_PER_YEAR, length, 1):
            df = self.make_indicators(idx)
            if df is None:
                break
            candle = df.iloc[-1]
            
            if state == stockData.TradingState.BUY:
                if self.bid_price(candle):
                    if transaction_simul:
                        bet_money = balance * min([kelly_rate, 1.0])
                        amount = transaction.set_bid(candle, bet_money)
                        if amount <= 0:
                            continue
                        temp = balance - (amount * candle['close'])
                        if temp <= 0:
                            continue
                        balance = temp
                    else:
                        amount = transaction.set_bid(candle)

                    state = stockData.TradingState.SELL
                        
            elif state == stockData.TradingState.SELL:
                if self.ask_price(candle):
                    transaction.set_ask(candle)
                    trading_statement.add_transaction(transaction)
     
                    if transaction_simul:
                        balance = balance + transaction.calc_final_money()
                        trading_statement.set_balance(balance)

                    transaction = Transaction()
                    state = stockData.TradingState.BUY
                    
        return trading_statement

    # 오늘 일자로 매수 신호 나왔나
    def bid_signal_today(self):
        df = self.make_indicators(-1)
        if df is None:
            return False
        
        candle = df.iloc[-1]
        if self.bid_price(candle):
            return True
        
        return False
    
    # 오늘 일자로 매도 신호 나왔나
    def ask_signal_today(self):
        df = self.make_indicators(-1)
        if df is None:
            return False
        
        candle = df.iloc[-1]
        if self.ask_price(candle):
            return True
        
        return False
    
    # 차트 출력해서 맞는지 검증
    def print_chart(self):
        pass

