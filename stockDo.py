import logger
import datetime
from datetime import datetime

import stockPredic as sp
from printChart import PrintChart
import util as u
from strategyFiveLine import FiveLineStockStrategy
from strategyBollenger import BollengerStockStrategy
from strategyMACD import MacdStockStrategy

class StockDo:
    def __init__(self, stock_market):
        self.stock_market_ = stock_market    

    def do(self):
        pass

class PredicStockDo(StockDo):
    def do(self):
        self.__predic()

    def __predic(self):
        sm = self.stock_market_
        # s&p 500 지수를 같이 참고로 예측
        if sm.config_.index_ticker_ not in sm.stock_pool_:
            logger.info("s&p 지수 로딩 실패")
            return
        
        stock_price_index = sm.stock_pool_[sm.config_.index_ticker_]

        recommand_buy = {}
        recommand_sell = {}
        for sd in sm.stock_pool_.values():
            model_name = sm.config_.name_ + '_' + sd.ticker_
            mm_predic = sp.StockPredic(sd, stock_price_index, model_name)
            predic = mm_predic.predic()   
            sd.predic_price_ = predic

            predic_price = predic[0]
            chart_file = PrintChart.saveFigure(sm.chart_dir_, sd, sm.DATE_FMT)

            now_date = sd.now_candle_time()
            now_price = sd.now_price()
            if now_price < predic_price:
                recommand_buy[sd.name_] = [now_date, now_price, predic_price, chart_file]
            else:
                recommand_sell[sd.name_] = [now_date, now_price, predic_price, chart_file]

        log = "### 상승 예감 ↑ 매수 추천\n"
        for name, data in recommand_buy.items():
            l = ("[%s]의 [%s]의 종가[%2.2f], 다음 예측[%2.2f], 상승률[%2.2f]\n" %
                    (name, data[0], data[1], data[2], u.calcRate(data[1], data[2])*100))
            sm.send_chart_log(l, data[3])
            log += l

        log = "### 하락 예감 ↓ 매도 추천 "
        for name, data in recommand_sell.items():
            l = ("[%s]의 [%s]의 종가[%2.2f], 다음 예측[%2.2f], 하락률[%2.2f]\n" %
                    (name, data[0], data[1], data[2], u.calcRate(data[1], data[2])*100))
            sm.send_chart_log(l, data[3])
            log += l

        sm.send_message(log)        
    
# 전략을 로딩, 조합해서 필터링 하는 역활
# 5선화음, 이평선등 기본만 구현해보기
class StrategyStockDo(PredicStockDo):
    strategy_ = [MacdStockStrategy, BollengerStockStrategy, FiveLineStockStrategy]
    trading_history_ = []
    bid_signal_ = []
    ask_signal_ = []

    def do(self):
        self.__clear()
        self.__evaluation()
        self.__print()        

    def back_test(self, strategy_template, sd, balance):
        strategy = strategy_template(stock_data=sd
                                     , char_dir=self.stock_market_.chart_dir_)
        
        trading_statement = strategy.back_test(balance=balance)
        # 텔레그램 전송을 위해 미리 차트 그리고 경로 설정
        strategy.print_chart()
        trading_statement.chart_path_ = strategy.chart_path_
        return trading_statement
    
    # 전략을 투입할시 승률을 구한다
    def __evaluation(self):
        sm = self.stock_market_
        balance = sm.config_.balance_
        for sd in sm.stock_pool_.values():
            for template in self.strategy_:
                if template.able_back_test_ == False:
                    continue
                trading_statement = self.back_test(strategy_template=template
                                                   ,sd = sd
                                                   ,balance=balance)
                if trading_statement is None:
                    continue

                if trading_statement.total_trading_count() == 0:
                    continue

                self.trading_history_.append(trading_statement)
                strategy = template(stock_data=sd, char_dir=self.stock_market_.chart_dir_)

                if strategy.bid_signal_today() == True:
                    self.bid_signal_.append(trading_statement)

                if strategy.ask_signal_today() == True:
                    self.ask_signal_.append(trading_statement)

    ## 결과 출력하기
    def __print(self):
        sm = self.stock_market_
        config = sm.config_
        all_print = config.print_all_
        now = datetime.now()
        log = "☆ 추세 확인 {0} - {1} ".format(sm.name_, now.strftime(sm.DATE_FMT))
        sm.send_message(log)
        
        for sd in sm.stock_pool_.values():
            for template in self.strategy_:
                strategy = template(stock_data=sd, char_dir=self.stock_market_.chart_dir_)
                strategy.print_chart()  
                log_text = "stock: {0}\nstrategy: {1}".format(sd.name_, strategy.__class__.__name__ )
                sm.send_chart_log(log_text, strategy.chart_path_)              

        log = "☆ 추천 {0} - {1}".format(sm.name_, now.strftime(sm.DATE_FMT))
        sm.send_message(log)

        # 전체 결과 출력
        for trading_statement in self.trading_history_:
            trading_statement.log() 
            trading_statement.print_excel()
 
        # 오늘 buy signal 출력
        for trading_statement in self.bid_signal_:
            sd = trading_statement.stock_data_
            if sd.having_ != 0 or all_print:
                log_summry = trading_statement.log_summry(info = "↑ ⓑⓤⓨ bid, 매수 ⓑⓤⓨ ↑")
                sm.send_chart_log(log_summry, trading_statement.chart_path_)
                logger.info(log_summry)
            #sm.send_message(log_summry)

        # 오늘 sell signal 출력
        for trading_statement in self.ask_signal_:
            sd = trading_statement.stock_data_            
            if sd.having_ != 0 or all_print:
                log_summry = trading_statement.log_summry(info = "↓ ⓢⓔⓛⓛ ask, 매도 ⓢⓔⓛⓛ ↓")
                sm.send_chart_log(log_summry, trading_statement.chart_path_)
                logger.info(log_summry)


    def __clear(self):
        self.trading_history_.clear()
        self.bid_signal_.clear()
        self.ask_signal_.clear()