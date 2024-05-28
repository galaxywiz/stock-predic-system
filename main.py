# pip install -r requirements.txt 
# 갱신시 pip freeze > requirements.txt
#=== 아이디어 ===#
# 1. 실제 주식 시장 처럼. 1일 1data 쌓는 형식으로 진행
#    데이터 시작은 5년전 부터 시작,
#    게임 시작은 3년전 부터 시작, -> 1일 1데이터 쌓기로 진행
# 2. agent 는 특정 금액만 가지고 buy / sell 로 주식 매수 매입
# 3. dqn 으로 agent 가 최적의 주식으로 돈을 가장 많이 버는 모델 만들어 보기
from datetime import datetime
from datetime import timedelta  
import time

import stockMaket
import config
# -----------------------------------------
# 메인 함수 시작
# 음.. 보는게 너무 힘든데, 텔레그램 체널 2,3개 연동 하도록 해야 할듯.
# 모니터닝용, 지금 보유용
if __name__ == '__main__':
    market_list = []
    test = True
    if test:
        # biancesMarket = stockMaket.StockMarket(
        #     config.BinanceStockMarketConfig(), real_trade=False)
        #config.USAStockMarketConfig.use_message_ = False
        #usaMarket = stockMaket.StockMarket(
        #    config.USAStockMarketConfig(), real_trade=False)
        koreaMarket = stockMaket.StockMarket(
            config.KoreaStockMarketConfig(), real_trade=False)
        #taiwanMarket = stockMaket.StockMarket(
        #     config.TaiwanStockMarketConfig(), real_trade=False)

        #market_list.append(usaMarket)
        market_list.append(koreaMarket)
        # market_list.append(taiwanMarket)
    else:
        usaMarket = stockMaket.StockMarket(
            config.USAStockMarketConfig(), real_trade=False)
        koreaMarket = stockMaket.StockMarket(
            config.KoreaStockMarketConfig(), real_trade=False)
        taiwanMarket = stockMaket.StockMarket(
            config.TaiwanStockMarketConfig(), real_trade=False)

        market_list.append(usaMarket)
        market_list.append(koreaMarket)
        market_list.append(taiwanMarket)

    if test:
        for market in market_list:
            market.check_strategy()
        #   market.predic_stock()
    else:  
        while(True):
            for market in market_list:
                market.do()

            time.sleep(1)
