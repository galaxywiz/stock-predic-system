import pandas as pd
import matplotlib.pyplot as plt
# 樂活五線譜 차트는 대만의 주식 투자자 LunaOwl이 개발한 기술입니다. 
# 이 차트는 주가의 움직임을 음악의 5선 음계와 유사한 5개의 선으로 나타냅니다. 
# 각 선은 주가의 지지와 저항을 나타내며, 주가가 이 선들을 넘어서면 주가의 움직임이 바뀔 가능성이 높습니다.

# 樂活五線譜 차트는 다음과 같이 사용됩니다.

# 주가가 지지선 아래로 떨어지면 매도 신호입니다.
# 주가가 저항선 위로 올라가면 매수 신호입니다.
# 주가가 지지선과 저항선 사이에 머무르면 관망 신호입니다.
# 樂活五線譜 차트는 다른 기술적 분석 도구와 함께 사용하면 주가의 움직임을 보다 정확하게 예측하는 데 도움이 될 수 있습니다.

# 樂活五線譜 차트는 다음과 같은 장점이 있습니다.

# 주가의 움직임을 직관적으로 이해할 수 있습니다.
# 다른 기술적 분석 도구와 함께 사용하면 주가의 움직임을 보다 정확하게 예측할 수 있습니다.
# 그러나 樂活五線譜 차트는 다음과 같은 단점도 있습니다.

# 주가의 움직임을 과거의 데이터로만 예측하기 때문에 미래의 주가 움직임을 정확하게 예측할 수 있는 것은 아닙니다.
# 다른 기술적 분석 도구와 마찬가지로, 樂活五線譜 차트도 완벽한 것은 아니며, 주가의 움직임을 잘못 예측할 수도 있습니다.
# 따라서 樂活五線譜 차트를 사용할 때는 다른 기술적 분석 도구와 함께 사용하고, 주가의 움직임을 예측할 때는 항상 신중을 기해야 합니다.

# 데이터를 가져옵니다.
df = pd.read_csv("data.csv")

# 5개의 선을 계산합니다.
high = df['High'].tolist()
low = df['Low'].tolist()
mid = (high + low) / 2
line1 = mid - 0.2 * (high - low)
line2 = mid - 0.4 * (high - low)
line3 = mid - 0.6 * (high - low)
line4 = mid - 0.8 * (high - low)
line5 = mid - 1 * (high - low)

# 차트를 그립니다.
plt.plot(df['date'], high)
plt.plot(df['date'], low)
plt.plot(df['date'], line1)
plt.plot(df['date'], line2)
plt.plot(df['date'], line3)
plt.plot(df['date'], line4)
plt.plot(df['date'], line5)

# 지지와 저항선을 표시합니다.
for i in range(1, 6):
    plt.axhline(i, color='black', linestyle='--')

# 레이블을 추가합니다.
plt.xlabel('Date')
plt.ylabel('Price')

# 차트를 보여줍니다.
plt.show()