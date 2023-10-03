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

class TradingStatement:
    def __init__(self, sd, trading_name):
        self.stock_data_ = sd
        self.transctions_ = []
        self.trading_name_ = trading_name

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

    def log(self):
        trading_count = self.total_trading_count()                    
        win_rate = self.win_rating()
        logger.info("! [%s][%s] 의 백테스팅 리포트" % (self.stock_data_.name_, self.trading_name_))
        for tran in self.transctions_:
            bid_candle = tran.bid_candle_
            ask_candle = tran.ask_candle_
            logger.info("- 매수[%s]:[%2.2f], 수량[%d], 매수 금액[%2.2f]" % (bid_candle["Date"], bid_candle["Close"], tran.amount_, bid_candle["Close"] * tran.amount_))
            logger.info("- 매도[%s]:[%2.2f], 수량[%d], 매도 금액[%2.2f]" % (ask_candle["Date"], ask_candle["Close"], tran.amount_, ask_candle["Close"] * tran.amount_))
            logger.info("- 이익[%2.2f]" % (tran.calc_profit()))

        logger.info("+ [%s][%s] 의 승률 %2.2f %%, 거래수 %d, 총이익 [%2.2f]" % (self.stock_data_.name_, self.trading_name_, win_rate * 100, trading_count, self.total_prtofit())) 
        return win_rate
