import os.path
import matplotlib.pyplot as plt
import stockData

class StockStrategy:
    def __init__(self, stock_data, char_dir):
        self.stock_data_ = stock_data
        self.char_dir_ = char_dir

    # 매수 가격인가?
    def bid_price(self, candle):
        pass

    # 매도 가격인가?
    def ask_price(self, candle):
        pass
    
    def back_test(self, balance = 0):
        df = self.stock_data_.chart_data_
        
        buy_price = 0
        profit = 0
        total_profit = 0
        win_rate = 0  
        win_count = 0      
        trading_count = 0

        state = stockData.TradingState.BUY
        for idx, candle in df.iterrows():
            now_price = candle["Close"]
            
            if state == stockData.TradingState.BUY:
                if self.bid_price(candle):
                    state = stockData.TradingState.SELL
                    buy_price = now_price
                    profit = 0
            elif state == stockData.TradingState.SELL:
                if self.ask_price(candle):
                    state = stockData.TradingState.BUY
                    profit = now_price - buy_price
                    buy_price = 0
                    
                    if profit > 0:
                        win_count = win_count + 1
                    trading_count = trading_count + 1
                    total_profit = total_profit + profit
                    
        if trading_count > 0:
            win_rate = win_count / trading_count
        print("%s 의 승률 %2.2f %%, 거래수 %d" % (self.stock_data_.name_, win_rate, trading_count)) 
        return win_rate

    # 차트 출력해서 맞는지 검증
    def print_chart(self):
        pass

class FiveLineStockStrategy(StockStrategy):
    def bid_price(self, candle):
        close = candle['Close']
        TL2SD = candle["TL-2SD"]
        if close < TL2SD:
            return True
        return False
    
    def ask_price(self, candle):
        close = candle['Close']
        TL2SD = candle["TL+2SD"]
        if close > TL2SD:
            return True
        return False
    
    def print_chart(self):
        sd = self.stock_data_
        # 데이터 프레임을 최근 120일로 슬라이싱합니다.
        df = sd.chart_data_ #tail(120)               
        # print(df)
        plt.close()
        # 한글 폰트 설정
        plt.rc('font', family='Malgun Gothic')   # 나눔 폰트를 사용하려면 해당 폰트 이름을 지정
        plt.figure(figsize=(16, 8))

        for i in ['Close', 'priceTL', 'TL-2SD', 'TL-SD', 'TL+SD', 'TL+2SD']:
            plt.plot(df['Date'], df[i], label=i)

        plt.xlabel("Date")
        plt.ylabel("Price")
        title = "%s(%s)" % (sd.name_, sd.ticker_)
        plt.title(title)

        # 범례 추가
        plt.legend()

        # 이미지 저장
        dir = self.char_dir_
        if not os.path.exists(dir):
            os.makedirs(dir)
        save_file = "%s/%s.png" % (dir, sd.name_)
        plt.savefig(save_file)
        plt.close()
      
        print("$ 차트 갱신 [%s] => [%s]" % (sd.name_, save_file))
        