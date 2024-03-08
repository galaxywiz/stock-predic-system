# a stock prediction assistant
#-----------------------------------
Write Python 3.12.2

#=== Program Behavior Structure ===#
1. Read stock data in specific markets (US, Korea, Taiwan, etc.) using Yahoo Finance, etc. (daily chart)
2. Renewed stock data after market close
3. Backtesting with specified trading algorithms (Lohas 5-line, MACD, Bollinger)
4. Find the winning rate and use the Kelly formula to calculate the optimal batting rate
5. Backtesting again with this batting ratio
6. Processing results and charts to be sent to the specified Telegram for daily confirmation.

# customization files
1. *_stock.txt
I have a list of Korean, Taiwanese, and American stocks.
The entry format is name:ticker:separate number
name is the value to view in the messenger
Ticker is the price of Tigger to be found in yahoo finance

2. config.py
Classes with Random Variables
Messenger alarms use Telegram and Line. Make each bot token and fill it in
telegram_token = "any token"
telegram_id = "any ID"
line_token = "line token"

=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# 주식 예측 도우미
#-----------------------------------
파이썬 3.12.2 로 작성

#=== 프로그램 동작 구조 ===#
1. 야후 파이낸스등을 사용하여 특정시장(미국, 한국, 대만등) 주식 데이터를 (1일봉 차트) 읽어들임
2. 장 마감이후 주식데이터 새로 갱신
3. 지정된 매매 알고리즘(로하스 5선, MACD, 볼린저) 로 백테스팅
4. 승률을 구해서, 이를 바탕으로 켈리 공식을 사용, 최적의 배팅 비율을 계산
5. 이 배팅비율로 다시 백테스팅
6. 결과와 차트를 지정된 텔레그램으로 보내서 매일 확일 할 수 있도록 처리.

# 커스터마이징 파일들
1. *_stock.txt
    지긍믄 한국, 대만, 미국 주식 리스트가 있음.
    기입포멧은 name:ticker:구분번호
    name 은 메신저에서 볼 값
    ticker 는 yahoo 파이낸스에서 찾을 티거값

2. config.py 
   임의 변수 모은 클래스
   메신저 알람은 텔레그램과, 라인을 사용. 각각 봇 토큰 만들어서 기입
      telegram_token = "임의 토큰"
      telegram_id = "임의 아이디"
      line_token = "라인 토큰"
  

