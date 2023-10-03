import logger
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
    strategy_ = [FiveLineStockStrategy, BollengerStockStrategy, MacdStockStrategy]

    def do(self):
        self.__calcWinRate()
        # self.__calcKellyFormula()        
        # self.__backTesting()
        self.__print()

    # 전략을 투입할시 승률을 구한다
    def __calcWinRate(self):
        sm = self.stock_market_
        for sd in sm.stock_pool_.values():
            for template in self.strategy_:
                strategy = template(stock_data=sd, char_dir=self.stock_market_.chart_dir_)
                trading_statement = strategy.back_test()
                trading_statement.log()
                
    
    # 해당 전략으로 최적의 배팅 비율을 구한다
    def __kelly_criterion(self, p, a, b):
        # 패배 확률 계산
        q = 1 - p
        # 최적 투자 비중 계산
        f = (p * (b + 1) - 1) / (a * b)
        # 결과 반환
        return f

    # # 예시 입력값
    # p = 0.6 # 승리 확률 60%
    # a = 0.1 # 패배시 손실률 10%
    # b = 0.2 # 승리시 수익률 20%

    # # 켈리공식 계산 함수 호출
    # f = kelly_criterion(p, a, b)

    # 백테스팅을 해본다.
    def __backTesting(self):
        pass

    ## 결과 출력하기
    def __print(self):
        sm = self.stock_market_
        for sd in sm.stock_pool_.values():
            for template in self.strategy_:
                strategy = template(stock_data=sd, char_dir=self.stock_market_.chart_dir_)
                strategy.print_chart()
 