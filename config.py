import configparser
import datetime as dt

from stockCrawler import USAStockCrawler, FutureCrawler, KoreaStockCrawler, TaiwanStockCrawler, BinanceCoinCrawler
from sqliteStockDB import DayPriceDB, DayPriceFloatDB, DayPreDB
from stockData import StockData, TradingState, StockType
from messenger import TelegramBot, LineBot
# 봇 설정
class StockMarketConfig:
    def __init__(self):
        self.load_config("config.conf")

    def set_config(self, config_file, cheader):
        config = configparser.ConfigParser()
        with open(config_file, 'r', encoding='utf-8') as f:
            config.read_file(f)      
        self.name_ = config[cheader]['name']
        #https://api.telegram.org/bot1911337440:AAEC0drjJeXOuXrxWm2SEifa6-b0uepv5vQ/getUpdates 로 id 얻어오기
        telegram_token = config[cheader]['telegram_token']
        telegram_id = config[cheader]['telegram_id']
        line_token = config[cheader]['line_token']

        # 여기서 메신저 선택 로직을 추가할 수 있습니다
        self.messenger_ = TelegramBot(token=telegram_token, id=telegram_id, name=self.name_)

        self.is_debug_ = config.getboolean(cheader, 'is_debug')
        self.DATE_FMT = config[cheader]['DATE_FMT']
        self.stock_type_ = getattr(StockType, config[cheader]['stock_type'])
        
        crawler = config[cheader]['crawler_type']
        if crawler == 'USAStockCrawler':
            self.crawler_ = USAStockCrawler()
        elif crawler == 'KoreaStockCrawler':
            self.crawler_ = KoreaStockCrawler()
        elif crawler == 'TaiwanStockCrawler':
            self.crawler_ = TaiwanStockCrawler()
        elif crawler == 'BinanceCoinCrawler':
            self.crawler_ = BinanceCoinCrawler()
            
        self.is_file_load_ = config.getboolean(cheader, 'is_file_load')
        self.list_file_name_ = config[cheader]['list_file_name']
        self.print_all_ = config.getboolean(cheader, 'print_all')
 
        self.index_ticker_ = config[cheader]['index_ticker']
        self.limit_list_size_ = config.getint(cheader, 'limit_list_size')
        self.prediction_ = config.getboolean(cheader, 'prediction')
        
        db_name = config[cheader]['day_price_db_name']
        db_table = config[cheader]['day_price_db_table']
        self.day_price_db_ = DayPriceFloatDB(db_name, db_table)

        pre_name = config[cheader]['day_pre_db_name']
        pre_table = config[cheader]['day_pre_db_table']
        self.day_pre_db_ = DayPreDB(pre_name, pre_table)    
    
        self.char_dir_ = config[cheader]['chart_dir']
        self.base_web_site_ = config[cheader]['base_web_site']
        self.balance_ = config.getint(cheader, 'balance')

        self.start_hour_ = config.getint(cheader, 'start_hour')
        self.start_min_ = config.getint(cheader, 'start_min')
        self.start_week_ = config[cheader]['start_week'].split(',')
        
    def crawling_time(self):
        now = dt.datetime.now()
        craw_time = dt.datetime(now.year, now.month, now.day, self.start_hour_, self.start_min_)
        return craw_time

#---------------------------------------------------------#
class USAStockMarketConfig(StockMarketConfig):
    def load_config(self, config_file):
        cheader = 'USAStockMarketConfig'
        self.set_config(config_file, cheader)        

#---------------------------------------------------------#
class KoreaStockMarketConfig(StockMarketConfig):
    def load_config(self, config_file):
        cheader = 'KoreaStockMarketConfig'
        self.set_config(config_file, cheader)  

#---------------------------------------------------------#
class TaiwanStockMarketConfig(StockMarketConfig):
    def load_config(self, config_file):
        cheader = 'TaiwanStockMarketConfig'
        self.set_config(config_file, cheader) 
    
#---------------------------------------------------------#
class BinanceStockMarketConfig(StockMarketConfig):
    def load_config(self, config_file):
        cheader = 'BinanceStockMarketConfig'
        self.set_config(config_file, cheader) 
