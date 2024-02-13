import pandas as pd
import numpy as np
import os.path
import logger

class Transaction:
    #매수
    def set_bid(self, candle, batting_money = 0):
        self.bid_candle_ = candle
        self.ask_candle_ = None
        self.amount_ = 0
        if batting_money == 0:
            return 0
        else:
            bid_price = self.bid_candle_['close']
            amount = int(batting_money / bid_price)
            if amount <= 0:
                return 0
            self.amount_ = amount

        return self.amount_
    #매도
    def set_ask(self, candle):
        self.ask_candle_ = candle

    def calc_profit(self):
        bid_price = self.bid_candle_['close']
        ask_price = self.ask_candle_['close']
        profit = ask_price - bid_price
        return profit * self.amount_
    
    def calc_final_money(self):
        ask_price = self.ask_candle_['close']
        return ask_price * self.amount_
    
    def calc_profit_rate(self):
        bid_price = self.bid_candle_['close']
        ask_price = self.ask_candle_['close']
        profit_rate = (ask_price - bid_price) / bid_price
        return profit_rate

class TradingStatement:
    def __init__(self, sd, trading, balance=0):
        self.stock_data_ = sd
        self.transactions_ = []
        self.balance_ = balance
        self.init_balance_ = balance

        self.trading_ = trading
        self.trading_name_ = trading.__class__.__name__
        self.chart_path_ = ""
        self.excel_file_ = ""

    def add_transaction(self, tran):
        self.transactions_.append(tran)

    def total_prtofit(self):
        profit = 0
        for tran in self.transactions_:
            profit += tran.calc_profit()
        return profit

    def total_trading_count(self):
        count = len(self.transactions_)
        return count

    # 승률
    def win_rating(self):
        trading_count = self.total_trading_count()
        if trading_count <= 0:
            return 0
        
        win_count = 0
        for tran in self.transactions_:
            if tran.calc_profit() > 0:
                win_count = win_count + 1
        
        win_rate = win_count / trading_count
        return win_rate

    # 수익율
    def profit_rate(self):
        trading_count = self.total_trading_count()
        if trading_count <= 0:
            return 0
        
        rate = 0
        for tran in self.transactions_:
            if tran.calc_profit() > 0:
                rate = rate + tran.calc_profit_rate()                
        
        rate = rate / trading_count
        return rate
    
    # 손실율
    def lose_rate(self):
        trading_count = self.total_trading_count()
        if trading_count <= 0:
            return 0
        
        rate = 0
        for tran in self.transactions_:
            if tran.calc_profit() <= 0:
                rate = rate + tran.calc_profit_rate()                
        
        rate = rate / trading_count
        return rate
    
    def set_balance(self, balance):
        self.balance_ = balance
    
    # 해당 전략으로 최적의 배팅 비율을 구한다
    def __kelly_criterion(self, p, profit, loss):
        if loss == 0:
  #          logger.info("켈리공식으로 손실율 0으론 계산 불가")
            return 0
        
        q = 1 - p
        b = profit / loss  # 이길 때 얻는 이익과 지면 손실 비율의 비율
        if b == 0:
 #           logger.info("켈리공식으로 이익, 손실 비율 0으론 계산 불가")
            return 0
        
        f_star = (p * b - q) / b
        return f_star
    
    def calc_kelly_rate(self):
        trading_count = self.total_trading_count() 
        if trading_count == 0:
            return 0
        win_rate = self.win_rating()
        profit_rate = self.profit_rate()
        lose_rate = self.lose_rate()
        f_star = self.__kelly_criterion(win_rate, profit_rate, lose_rate)
        return f_star
    
    def log_summry(self, info = ""):
        trading_count = self.total_trading_count() 
        ticker_name = self.stock_data_.name_
        if trading_count <= 0:
            log = "! [%s][%s] 의 백테스팅 거래 없음" % (ticker_name, self.trading_name_)
            return log
        
        win_rate = self.win_rating()
        profit_rate = self.profit_rate()
        lose_rate = self.lose_rate()
        kelly_rate = self.calc_kelly_rate()

        sd = self.stock_data_
        last_candle = sd.chart_data_.iloc[-1]
        first_candle = sd.chart_data_.iloc[0]
        log = ""
        
        now_price = float(last_candle['close'])
        if len(info) > 1:
            log += "——————————————————\n"
            log += "SIGNAL:[{0}]\n".format(info)
            log += "종목:[{0}]\n".format(ticker_name)
            log += "전략:[{0}] in [{1}] close[{2}]\n".format( self.trading_name_, last_candle['date'], now_price)
            log += "매수시 배팅율 [{0:.2f}]%\n".format(kelly_rate * 100)
            log += " => 10000 일경우 배팅금 [{0:.2f}]\n".format(10000 * kelly_rate)
            log += "——————————————————\n"

        log += "! [{0}][{1}] 의 백테스팅 리포트\n".format(self.stock_data_.name_, self.trading_name_)      
        log += "+ [{0}] ~ [{1}] 기간.\n".format(first_candle['date'], last_candle['date'])
        log += "+ 자본금[{0:,.2f}] -> 총이익[{1:,.2f}]\n".format(self.init_balance_, self.total_prtofit())
        log += "+ 승률[{0:.2f}]%, 총거래수[{1}]\n".format(win_rate * 100, trading_count)
        log += "+ 수익율[{0:.2f}]%, 손실율[{1:.2f}]%, 최적배팅[{2:.2f}]%\n".format(profit_rate * 100, lose_rate * 100, kelly_rate * 100)
        log += "+ [{0:.2f}]% 비율 배팅 시뮬시 => 총 금액[{1:,.2f}]\n".format(kelly_rate * 100, self.balance_)
     
        first_price = float(first_candle['close'])
        init_amount = int(self.init_balance_ / first_price)
        log += "+ 만약 당시 [{0:,.2f}]을 투자후 매매 안했다면 [{1}] 개 보유\n".format(self.init_balance_, init_amount)
        log += "+ 지금 가치 [{0}]개는 [{1:,.2f}]$\n".format(init_amount, init_amount * now_price)
        return log
        
    def log(self):
        trading_count = self.total_trading_count() 
        if trading_count <= 0:
            logger.info("! [%s][%s] 의 백테스팅 거래 없음" % (self.stock_data_.name_, self.trading_name_))                       
            return
        
        logger.info(self.log_summry())        
        #엑셀에 뽑을 수 있도록 
        logger.info("|매수일|매수종가|수량|매수가격|매도일|매도종가|수량|매도가격|이익")
        for tran in self.transactions_:
            bid_candle = tran.bid_candle_
            ask_candle = tran.ask_candle_
            logger.info("|{0}|{1:,.2f}|{2}|{3:,.2f}|{4}|{5:,.2f}|{6}|{7:,.2f}|{8:,.2f}"
                        .format(bid_candle['date'], bid_candle['close'], tran.amount_, bid_candle['close'] * tran.amount_
                            , ask_candle['date'], ask_candle['close'], tran.amount_, ask_candle['close'] * tran.amount_
                            , tran.calc_profit()))

    def print_excel(self):
        bid_date = []
        bid_price = []
        amount = []
        ask_date = []
        ask_price = []
        profit = []
        
        for tran in self.transactions_:
            bid_candle = tran.bid_candle_
            ask_candle = tran.ask_candle_
            bid_date.append(bid_candle['date'])
            bid_price.append(bid_candle['close'])
            ask_date.append(ask_candle['date'])
            ask_price.append(ask_candle['close'])
            amount.append(tran.amount_)
            profit.append(tran.calc_profit())

        data = {
            'bid date': bid_date,
            'bid price': bid_price,
            'bid amount': amount,
            'purchase amount': np.array(bid_price) * np.array(amount),  # 수정
            'ask date': ask_date,
            'ask price': ask_price,
            'ask amount': amount,
            'selling amount': np.array(ask_price) * np.array(amount),  # 수정
            'profit': profit
        }
        df_backtesting = pd.DataFrame(data)     

        # 결과 요약 텍스트
        result_summary = self.log_summry()
        result_summary_lines = result_summary.split('\n')

        # 데이터프레임 생성
        df_backtesting = pd.DataFrame(data)
        df_summary = pd.DataFrame({'Summary': result_summary_lines})

        dir = "./excel"
        if not os.path.exists(dir):
            os.makedirs(dir)
        sd = self.stock_data_
        df_chart_data = sd.chart_data_
        self.excel_file_ = "%s/%s_%s.xlsx" % (dir, sd.name_, self.trading_name_)
        with pd.ExcelWriter(self.excel_file_, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            df_backtesting.to_excel(writer, sheet_name='Back testing', index=False)
            df_chart_data.to_excel(writer, sheet_name='Chart Data', index=False)
