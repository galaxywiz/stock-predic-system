# 필요한 모듈 임포트
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client

# 바이낸스 API 키와 시크릿 키 입력
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

# 바이낸스 클라이언트 객체 생성
client = Client(api_key, api_secret)

# 거래할 심볼과 매매 조건 설정
symbol = "BTCUSDT" # 비트코인/USDT
interval = "1h" # 1시간 간격의 캔들스틱 데이터
short_window = 12 # 단기 이동평균선 윈도우 크기
long_window = 26 # 장기 이동평균선 윈도우 크기
signal_window = 9 # MACD 신호선 윈도우 크기

# MACD 계산 함수 정의
def macd(df, short_window, long_window, signal_window):
    # 종가 기준으로 단기 이동평균선 계산
    df["short_ema"] = df['close'].ewm(span=short_window).mean()
    # 종가 기준으로 장기 이동평균선 계산
    df["long_ema"] = df['close'].ewm(span=long_window).mean()
    # MACD 값 계산
    df["MACD"] = df["short_ema"] - df["long_ema"]
    # MACD 신호선 값 계산
    df["MACD_signal"] = df["MACD"].ewm(span=signal_window).mean()
    return df

# 캔들스틱 데이터 가져오기 (최근 500개)
klines = client.get_historical_klines(symbol, interval, "500 hours ago UTC")

# 데이터프레임으로 변환
df = pd.DataFrame(klines)
df.columns = ["open_time", 'open', 'high', 'low', 'close', 'volume', "close_time", "qav", "num_trades", "taker_base_vol", "taker_quote_vol", "is_best_match"]

# 가격과 거래량 데이터만 남기고 나머지 열 삭제
df = df[['open', 'high', 'low', 'close', 'volume']]

# 가격 데이터 타입을 실수형으로 변환
df = df.astype(float)

# MACD 계산
df = macd(df, short_window, long_window, signal_window)

# 그래프 그리기
plt.figure(figsize=(15,10)) # 그래프 크기 설정
plt.plot(df.index, df['close'], label='Price') # 종가 그래프 그리기
plt.plot(df.index, df['MACD'], label='MACD') # MACD 그래프 그리기
plt.plot(df.index, df['MACD_signal'], label='MACD Signal') # MACD 신호선 그래프 그리기
plt.legend(loc='upper left') # 범례 위치 설정
plt.title('MACD Chart') # 제목 설정
plt.xlabel('Time') # x축 라벨 설정
plt.ylabel('Price') # y축 라벨 설정
plt.show() # 그래프 출력
