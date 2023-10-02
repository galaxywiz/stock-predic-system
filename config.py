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

    def crawling_time(self):
        now = time.localtime()
        start_hour = 14
        start_min = 30
        if now.tm_wday < 5:
            if now.tm_hour == start_hour and now.tm_min >= start_min: 
                return True
        return False