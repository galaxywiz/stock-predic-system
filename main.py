#----------------------------------------------#
# 파이토치를 위해 아나콘다창에서 관리자 권한 인스톨해야 함
#----------------------------------------------#
# 설치시 노트북 환경에 따라
# conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch -y
# conda install pytorch torchvision torchaudio cpuonly -c pytorch -y

# conda create --name env32bit --file anaconda-pkg.txt

# 설치 실패시 아래 실행
# conda install -c conda-forge ta-lib -y
# conda install -c postelrich yahoo-finance
# conda install -c anaconda pandas-datareader -y
# conda install -c conda-forge python-telegram-bot -y
# conda install scikit-learn -y

# pip install telepot yahoo-finance
# pip install logger
# pip3 install -U scikit-learn scipy matplotlib
# pip install yfinance
# pip install cufflinks
# pip install chart_studio
# pip install plotly
# pip install plotly==5.3.1
# pip install -U kaleido
# pip install kaleido==0.1.0post1
# pip install apscheduler
#=== 아이디어 ===#
# 1. 실제 주식 시장 처럼. 1일 1data 쌓는 형식으로 진행
#    데이터 시작은 5년전 부터 시작,
#    게임 시작은 3년전 부터 시작, -> 1일 1데이터 쌓기로 진행
# 2. agent 는 특정 금액만 가지고 buy / sell 로 주식 매수 매입
# 3. dqn 으로 agent 가 최적의 주식으로 돈을 가장 많이 버는 모델 만들어 보기

import time
import stockMaket
import config
# -----------------------------------------
# 메인 함수 시작
if __name__ == '__main__':
    botList = []
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
      bot.predic_stock()
      
    while(True):
        now = time.localtime()
        for stockMarket in botList:
            stockMarket.do()

        time.sleep(1)
