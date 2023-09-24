import logger
import stockPredic as sp
from printChart import PrintChart
import util as u
from stockData import StockData, BuyState, StockType
import stockMaket

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
            model_name = sm.config_.name_ + '_' + sd.name_
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
    

class StrategyStockDo(PredicStockDo):
    pass