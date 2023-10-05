from datetime import datetime
from datetime import timedelta
import time

from stockCrawler import USAStockCrawler, FutureCrawler, KoreaStockCrawler, TaiwanStockCrawler
from sqliteStockDB import DayPriceDB, DayPriceFloatDB, DayPreDB
from stockData import StockData, TradingState, StockType
from messenger import TelegramBot, LineBot
# 봇 설정
class StockMarketConfig:
    def crawling_time(self):
        pass

#---------------------------------------------------------#
class USAStockMarketConfig(StockMarketConfig):
    def __init__(self):
        self.name_ = "USA"
        telegram_token = "임의 토큰"
        telegram_id = "임의 아이디"
        line_token = "라인 토큰"
        self.messenger_ = LineBot(token = line_token, id = telegram_id, name = self.name_)
        #self.messenger_ = TelegramBot(token = telegram_token, id = telegram_id, name = self.name_)

        self.is_debug_ = False
        self.DATE_FMT = "%Y-%m-%d"
        self.stock_type_ = StockType.STOCK_USA

        self.crawler_ = USAStockCrawler()
        self.is_file_load_ = True
        self.list_file_name_ = "list_usa_stock.txt"
        self.index_ticker_ = "SNP500"
        self.limit_list_size_ = 200
        self.prediction_ = True

        self.day_price_db_ = DayPriceFloatDB("USAStockData.db","day_price")
        self.day_pre_db_ = DayPreDB("USADayPre.db", "TODAY_STOCK_LIST")    
    
        self.char_dir_ = "chart_USA/"
        self.base_web_site_ = "https://finance.yahoo.com/quote/%s"
        self.time_frame_ = 5
        self.balance_ = 10000

    def crawling_time(self):
        now = time.localtime()
        start_hour = 7
        start_min = 0
        if 0 < now.tm_wday and now.tm_wday < 6:
            if now.tm_hour == start_hour and now.tm_min >= start_min: 
                return True
        return False

#---------------------------------------------------------#
class KoreaStockMarketConfig(StockMarketConfig):
    def __init__(self):
        self.name_ = "Korea"

        telegram_token = "임의 토큰"
        telegram_id = "임의 아이디"
        line_token = "라인 토큰"
        self.messenger_ = LineBot(token = line_token, id = telegram_id, name = self.name_)
       # self.messenger_ = TelegramBot(token = telegram_token, id = telegram_id, name = self.name_)

        self.is_debug_ = False
        self.DATE_FMT = "%Y-%m-%d"
        self.stock_type_ = StockType.STOCK_KOREA

        self.crawler_ = KoreaStockCrawler()
        self.is_file_load_ = True
        self.list_file_name_ = "list_korea_stock.txt"
        self.index_ticker_ = "코스피"

        self.limit_list_size_ = 250
        self.prediction_ = True

        self.day_price_db_ = DayPriceDB("KoreaStockData.db", "day_price")
        self.day_pre_db_ = DayPreDB("KoreaDayPre.db", "TODAY_STOCK_LIST")
       
        self.char_dir_ = "chart_Korea/"
        self.base_web_site_ = "http://finance.daum.net/quotes/A%s"
        self.time_frame_ = 5
        self.balance_ = 10000000

    def crawling_time(self):
        now = time.localtime()
        start_hour = 16
        start_min = 30
        if now.tm_wday < 5:
            if now.tm_hour == start_hour and now.tm_min >= start_min: 
                return True
        return False

class TaiwanStockMarketConfig(StockMarketConfig):
    def __init__(self):
        self.name_ = "Taiwan"

        telegram_token = "임의 토큰"
        telegram_id = "임의 아이디"
        line_token = "라인 토큰"
        #self.messenger_ = LineBot(token = line_token, id = telegram_id, name = self.name_)
        self.messenger_ = TelegramBot(token = telegram_token, id = telegram_id, name = self.name_)

        self.is_debug_ = False
        self.DATE_FMT = "%Y-%m-%d"
        self.stock_type_ = StockType.STOCK_KOREA

        self.crawler_ = TaiwanStockCrawler()
        self.is_file_load_ = True
        self.list_file_name_ = "list_taiwan_stock.txt"
        self.index_ticker_ = "上市"

        self.limit_list_size_ = 250
        self.prediction_ = True

        self.day_price_db_ = DayPriceDB("TaiwanStockData.db", "day_price")
        self.day_pre_db_ = DayPreDB("TaiwanDayPre.db", "TODAY_STOCK_LIST")
       
        self.char_dir_ = "chart_Taiwan/"
        self.base_web_site_ = "https://finance.yahoo.com/quote/%s"
        self.time_frame_ = 5
        self.balance_ = 250000

    def crawling_time(self):
        now = time.localtime()
        start_hour = 14
        start_min = 30
        if now.tm_wday < 5:
            if now.tm_hour == start_hour and now.tm_min >= start_min: 
                return True
        return False
    
#---------------------------------------------------------#
class UpbitStockMarketConfig(StockMarketConfig):
    def __init__(self):
        self.telegram_token_ = "1279149095:AAFCvfUi_6f7Cqf0cE6cRpQhyhODp06JPpQ"
        self.telegram_id_ = "508897948"  ## 행복의 예보 채널 아이디
        self.is_debug_ = False
        self.DATE_FMT = "%Y-%m-%d %H:%M:%S"
        self.stock_type_ = StockType.BITCOIN

        self.crawler_ = UpbitCoinCrawler()
        self.is_file_load_ = True
        self.list_file_name_ = "list_coin.txt"

        self.strategy_ = MACDTradeStrategy()
        self.limit_list_size_ = -1
        self.prediction_ = False

        self.day_price_db_ = DayPriceFloatDB("CoinData.db", "day_price")
        self.day_pre_db_ = DayPreDB("CoinDayPre.db", "TODAY_STOCK_LIST")    

        self.char_dir_ = "chart_coins/"
        self.base_web_site_ = "https://upbit.com/exchange?code=CRIX.UPBIT.KRW-%s"
        self.time_frame_ = 5

    def crawling_time(self):
        now = time.localtime()
        if (now.tm_min % 30) == 0: 
            return True
        return False

#---------------------------------------------------------#
class BinanceStockMarketConfig(StockMarketConfig):
    def __init__(self):
        self.telegram_token_ = "1807903004:AAE6PEWcccwrOO8Q8hY7u6vqZs7zQlRt8r4"
        self.telegram_id_ = "508897948" 
        self.DATE_FMT = "%Y-%m-%d %H:%M:%S"
        self.stock_type_ = StockType.BITCOIN

        self.market_key = "txSeICeVxYgm2Sy8ECAuteNo1DqhTSmGXzd93QEoYgvOhYXCECADkI77SR2GNEyO"
        self.market_secret = "oxK8JqhTP5ySr9i9ZjNpBjyT1780dQok9NYdyrODES8Ll8mLRyPIyrGNdchspCJa"
        self.crawler_ = BinanceCoinCrawler()
        self.is_file_load_ = False
        self.list_file_name_ = "list_binance_coin.txt"

        self.strategy_ = LarryRTradeStrategy()
        self.limit_list_size_ = -1
        self.prediction_ = False

        self.day_price_db_ = DayPriceFloatDB("BinanceCoinData.db", "day_price")
        self.day_pre_db_ = DayPreDB("BinanceCoinDayPre.db", "TODAY_STOCK_LIST")    

        self.char_dir_ = "chart_coins/"
        self.base_web_site_ = "https://www.binance.com/ko/trade/%s"
        self.time_frame_ = 3        # 3분은 너무 손해 보는거 같다 15분정도로
        self.is_debug_ = True

    def crawling_time(self):
        now = time.localtime()
        if (now.tm_min % self.time_frame_) == 0: 
            return True
        return False
