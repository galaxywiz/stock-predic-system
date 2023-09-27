import pandas as pd
import matplotlib.pyplot as plt
import stockData

class StockStrategy:
    def __init__(self, sd):
        self.stock_data_ = sd

    # 매수 가격인가?
    def bid_price(self):
        pass

    # 매도 가격인가?
    def ask_price(self):
        pass
    
    # 차트 출력해서 맞는지 검증
    def print_chart(self):
        pass

class FiveLineStockStrategy(StockStrategy):
    def bid_price(self):
        
        return super().bid_price()
    
    def ask_price(self):

        return super().ask_price()
    
    def print_chart(self):
        df = self.stock_data_
        plt.plot(df['Date'], df['High'])
        plt.plot(df['Date'], df['Low'])
        plt.plot(df['Date'], df['line1'])
        plt.plot(df['Date'], df['line2'])
        plt.plot(df['Date'], df['line3'])
        plt.plot(df['Date'], df['line4'])
        plt.plot(df['Date'], df['line5'])

        # 지지와 저항선을 표시합니다.
        for i in range(1, 6):
            plt.axhline(i, color='black', linestyle='--')

        # 레이블을 추가합니다.
        plt.xlabel('Date')
        plt.ylabel('Price')

        # 차트를 보여줍니다.
        plt.show()
        plt.savefig(df.name_+".png")
