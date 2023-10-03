import stockData
import logger

class Transaction:
    def set_bid(self, candle, amount = 1):
        self.bid_candle_ = candle
        self.ask_candle_ = None
        self.amount_ = amount

    def set_ask(self, candle):
        self.ask_candle_ = candle

    def calc_profit(self):
        bid_price = self.bid_candle_["Close"]
        ask_price = self.ask_candle_["Close"]
        profit = ask_price - bid_price
        return profit * self.amount_

    def calc_profit_rate(self):
        bid_price = self.bid_candle_["Close"]
        ask_price = self.ask_candle_["Close"]
        profit_rate = (ask_price - bid_price) / bid_price
        return profit_rate

class TradingStatement:
    def __init__(self, sd, trading):
        self.stock_data_ = sd
        self.transctions_ = []
        self.trading = trading
        self.trading_name_ = trading.__class__.__name__

    def add_transaction(self, tran):
        self.transctions_.append(tran)

    def total_prtofit(self):
        profit = 0
        for tran in self.transctions_:
            profit += tran.calc_profit()
        return profit

    def total_trading_count(self):
        count = len(self.transctions_)
        return count

    # 승률
    def win_rating(self):
        trading_count = self.total_trading_count()
        if trading_count <= 0:
            return 0
        
        win_count = 0
        for tran in self.transctions_:
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
        for tran in self.transctions_:
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
        for tran in self.transctions_:
            if tran.calc_profit() <= 0:
                rate = rate + tran.calc_profit_rate()                
        
        rate = rate / trading_count
        return rate
    
    # 해당 전략으로 최적의 배팅 비율을 구한다
    def __kelly_criterion(self, p, a, b):
        # 패배 확률 계산
        q = 1 - p
        # 최적 투자 비중 계산
        f = (p * (b + 1) - 1) / (a * b)
        # 결과 반환
        return f
       
    def log(self):
        trading_count = self.total_trading_count() 
        if trading_count <= 0:
            logger.info("! [%s][%s] 의 백테스팅 거래 없음" % (self.stock_data_.name_, self.trading_name_))                       
            return
        
        win_rate = self.win_rating()
        profit_rate = self.profit_rate()
        lose_rate = self.lose_rate()
        k = self.__kelly_criterion(win_rate, lose_rate, profit_rate)

        logger.info("! [%s][%s] 의 백테스팅 리포트" % (self.stock_data_.name_, self.trading_name_))
        for tran in self.transctions_:
            bid_candle = tran.bid_candle_
            ask_candle = tran.ask_candle_
            logger.info("- 매수[%s]:[%2.2f], 수량[%d], 매수 금액[%2.2f]" % (bid_candle["Date"], bid_candle["Close"], tran.amount_, bid_candle["Close"] * tran.amount_))
            logger.info("- 매도[%s]:[%2.2f], 수량[%d], 매도 금액[%2.2f]" % (ask_candle["Date"], ask_candle["Close"], tran.amount_, ask_candle["Close"] * tran.amount_))
            logger.info("- 이익[%2.2f]" % (tran.calc_profit()))

        logger.info("+ [%s][%s] 의 승률 %2.2f %%, 거래수 %d, 총이익 [%2.2f]" % (self.stock_data_.name_, self.trading_name_, win_rate * 100, trading_count, self.total_prtofit())) 
        logger.info("+ [%2.2f]%% 승률, [%2.2f]%% 수익율, [%2.2f]%% 손실율, [%2.2f]%%, 최적 배팅 비율" % (
            win_rate, profit_rate, lose_rate, k
        ))
        
