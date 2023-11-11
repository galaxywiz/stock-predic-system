from stockData import TradingState
import talib.abstract as ta
from talib import MA_Type
from tradingStatment import Transaction, TradingStatement

class StockStrategy:
    chart_path_ = ""
    chart_len_ = 100
    able_back_test_ = True

    def __init__(self, stock_data, char_dir):
        self.stock_data_ = stock_data
        self.char_dir_ = char_dir

    # 전략 만들기
    def make_indicators(self, start = 0, end = 0):
        sd = self.stock_data_
        if start < 0:
            start = 0

        lenth = len(sd.chart_data_)
        if end > 0:
            if lenth < end:
                return None
            df = sd.chart_data_[start:end]  
        else:
            df = sd.chart_data_
        return df

    # 매수 가격인가?
    def bid_price(self, candle):
        pass

    # 매도 가격인가?
    def ask_price(self, candle):
        pass
    
    #신호 보기. 신호가 당일 종가라...      
    def __check_singal(self, candle, signal_state):    
        if signal_state == TradingState.BUY:
            if self.bid_price(candle):
                return TradingState.BUY

        elif signal_state == TradingState.SELL:
            if self.ask_price(candle):
                return TradingState.SELL
                
        return TradingState.STAY

    # kelly_rate 를 매 순간 마다 계산 해 보는게 좋을듯...
    def calc_kelly_rate(self, df):
        trading_statement = TradingStatement(sd=self.stock_data_
                                             ,trading=self)

        transaction = Transaction()
        signal_state = TradingState.BUY
        trade_state = TradingState.STAY
        
        # DataFrame의 각 행을 순회
        for index, row in df.iterrows():
            candle = row
            
            #신호 보기. 신호가 당일 종가라...      
            if trade_state == TradingState.STAY:      
                trade_state = self.__check_singal(candle, signal_state)
                continue                

            # 신호가 나오면 다음날 매매함.
            elif trade_state == TradingState.BUY:
                transaction.set_bid(candle, batting_money=candle['close'])
                signal_state = TradingState.SELL
                trade_state = TradingState.STAY
                continue

            elif trade_state == TradingState.SELL:
                transaction.set_ask(candle)
                trading_statement.add_transaction(transaction)
     
                transaction = Transaction()     # 트렌젝션 초기화
                signal_state = TradingState.BUY
                trade_state = TradingState.STAY
                continue

        kelly_rate = trading_statement.calc_kelly_rate()
        return kelly_rate
    
    # kelly_rate 를 매 순간 마다 계산 해 보는게 좋을듯...
    def back_test(self, balance=0):
        df = self.stock_data_.chart_data_
        length = len(df)

        trading_statement = TradingStatement(sd=self.stock_data_
                                            ,trading=self
                                            ,balance=balance)
        transaction = Transaction()
        signal_state = TradingState.BUY
        trade_state = TradingState.STAY

        # data 는 1년 후 (working 220일) 지표가 정상적으로 로딩 된다
        # 1회차 -> 10년전 ~9년전, 2회차 10년전 ~ 9년1일차 ..... n차 10년전 ~ 오늘
        WORKING_DAY_PER_YEAR = 220
        for idx in range(WORKING_DAY_PER_YEAR, length, 1):
            df = self.make_indicators(end = idx)
            if df is None:
                break
            candle = df.iloc[-1]
            
            #신호 보기. 신호가 당일 종가라...      
            if trade_state == TradingState.STAY:      
                trade_state = self.__check_singal(candle, signal_state)
                continue                

            # 신호가 나오면 다음날 매매함.
            elif trade_state == TradingState.BUY:
                # 지금 데이터 만으로 kelly_rate를 구해야 정확함.
                # 백테스팅, 미래의 data를 모르므로 구매 당시 차트로 kelly_rate 계산
                kelly_rate = self.calc_kelly_rate(df)

                bet_money = balance * min([kelly_rate, 1.0])
                amount = transaction.set_bid(candle, bet_money)
                if amount <= 0:
                    continue
                temp = balance - (amount * candle['close'])
                if temp <= 0:
                    continue
                balance = temp
               
                signal_state = TradingState.SELL
                trade_state = TradingState.STAY
                continue

            elif trade_state == TradingState.SELL:
                transaction.set_ask(candle)
                trading_statement.add_transaction(transaction)
     
                balance = balance + transaction.calc_final_money()
                trading_statement.set_balance(balance)

                transaction = Transaction()     # 트렌젝션 초기화
                signal_state = TradingState.BUY
                trade_state = TradingState.STAY
                continue
        
        return trading_statement

    # 오늘 일자로 매수 신호 나왔나
    def bid_signal_today(self):
        df = self.make_indicators(end = -1)
        if df is None:
            return False
        
        candle = df.iloc[-1]
        if self.bid_price(candle):
            return True
        
        return False
    
    # 오늘 일자로 매도 신호 나왔나
    def ask_signal_today(self):
        df = self.make_indicators(end = -1)
        if df is None:
            return False
        
        candle = df.iloc[-1]
        if self.ask_price(candle):
            return True
        
        return False
    
    # 차트 출력해서 맞는지 검증
    def print_chart(self):
        pass

