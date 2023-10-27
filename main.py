# pip install -r requirements.txt 
# 갱신시 pip freeze > requirements.txt
#=== 아이디어 ===#
# 1. 실제 주식 시장 처럼. 1일 1data 쌓는 형식으로 진행
#    데이터 시작은 5년전 부터 시작,
#    게임 시작은 3년전 부터 시작, -> 1일 1데이터 쌓기로 진행
# 2. agent 는 특정 금액만 가지고 buy / sell 로 주식 매수 매입
# 3. dqn 으로 agent 가 최적의 주식으로 돈을 가장 많이 버는 모델 만들어 보기

import stockMaket
import config
# -----------------------------------------
# 메인 함수 시작
if __name__ == '__main__':
    botList = []
    test = False
    if test:
        # biancesMarket = stockMaket.StockMarket(
        #     config.BinanceStockMarketConfig(), real_trade=False)
        
        market = stockMaket.StockMarket(
            config.USAStockMarketConfig(), real_trade=False)

    #    botList.append(biancesMarket)
        botList.append(market)
    else:
        usaMarket = stockMaket.StockMarket(
            config.USAStockMarketConfig(), real_trade=False)
        koreaMarket = stockMaket.StockMarket(
            config.KoreaStockMarketConfig(), real_trade=False)
        taiwanMarket = stockMaket.StockMarket(
            config.TaiwanStockMarketConfig(), real_trade=False)
        
        botList.append(usaMarket)
        botList.append(koreaMarket)
        botList.append(taiwanMarket)

    for bot in botList:
        bot.check_strategy()
    #    bot.predic_stock()
      
    # while(True):
    #     now = time.localtime()
    #     for stockMarket in botList:
    #         stockMarket.do()

    #     time.sleep(1)
