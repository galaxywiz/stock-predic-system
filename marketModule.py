from enum import Enum
import ccxt

import logging
import traceback

from util import SingletonInstane

class MarketName (Enum):
    BINANCE = 0
    UPBIT = 1

#https://wikidocs.net/120396 이거 참고
##-----------------------------------
# cctx 라고 암호화폐 시장 모듈 사용
class MarketModule (SingletonInstane):
    market_ = ccxt.binance()

    def set_market(self, market_name, time_frame, api_key, secret):
        ORDER_EXPIRE_SEC = 60 * time_frame
        if market_name == MarketName.UPBIT:
            self.market_ = ccxt.upbit(config={
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True,
                'options' : {
                    'api-expires' : ORDER_EXPIRE_SEC
                    },
                })
        elif market_name == MarketName.BINANCE:
            self.market_ = ccxt.binance(config={
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True,
                'options' : {
                    'api-expires' : ORDER_EXPIRE_SEC
                    },
                })
        else:
            print("정의되지 않은 시장")

    def market(self):
        return self.market_

    def org_ticker(self, ticker):
        org_ticker = str(ticker).replace('_','/')
        return org_ticker

    def buy_order(self, ticker, amount):
        try:
            ticker = self.org_ticker(ticker)
            order = self.market_.create_market_buy_order(ticker, float(amount))
            print(order)
            return order
        except:
            logging.error(traceback.format_exc())
            logging.error("param ticker:%s, amount:%s" % (ticker, amount))
            return None

    def buy_order_limit(self, ticker, amount, price):
        try:
            ticker = self.org_ticker(ticker)
            order = self.market_.create_limit_buy_order(ticker, float(amount), price)
            print(order)
            return order
        except:
            logging.error(traceback.format_exc())
            logging.error("param ticker:%s, amount:%s, price:%s" % (ticker, amount, price))
            return None

    def sell_order(self, ticker, amount):
        try:
            ticker = self.org_ticker(ticker)
            order = self.market_.create_market_sell_order(ticker, float(amount))
            print(order)
            return order
        except:
            logging.error(traceback.format_exc())
            logging.error("param ticker:%s, amount:%s" % (ticker, amount))

            return None

    def sell_order_limit(self, ticker, amount, price):
        try:
            ticker = self.org_ticker(ticker)
            order = self.market_.create_limit_sell_order(ticker, float(amount), price)
            print(order)
            return order
        except:
            logging.error(traceback.format_exc())
            logging.error("param ticker:%s, amount:%s, price:%s" % (ticker, amount, price))
            return None

    def order_cancle(self, order, ticker):
        try:
            if order == 0:
                return 
            ticker = self.org_ticker(ticker)
            self.market_.cancel_order(order, ticker)
        except:
            logging.error(traceback.format_exc())

    def order_all_cancle(self):
        try:
            self.market_.cancel_all_orders() 
        except:
            logging.error(traceback.format_exc())

    def now_btc_price(self):
        try:
            info = self.market_.fetch_ticker('BTC/USDT')
            return info['close']
        except:
            logging.error(traceback.format_exc())
            return 0

    def now_price(self, ticker):
        try:
            ticker = self.org_ticker(ticker)
            info = self.market_.fetch_ticker(ticker)
            return info['close']
        except:
            return 0
            
    def load_btc_balance(self):
        balance = self.market_.fetch_balance()
        return balance
    ##-----------------------------------
