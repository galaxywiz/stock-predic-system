import pandas as pd
import matplotlib.pyplot as plt

class Backtest:
    def __init__(self, stock_strategy, initial_capital=1000000, commission=0.0015, slippage=0.005):
        self.stock_strategy_ = stock_strategy # 주식 전략 객체
        self.initial_capital_ = initial_capital # 초기 자본
        self.commission_ = commission # 수수료 비율
        self.slippage_ = slippage # 슬리피지 비율
        self.stock_data_ = stock_strategy.stock_data_ # 주식 데이터
        self.signals_ = pd.DataFrame(index=self.stock_data_.index) # 매수/매도 신호 데이터프레임
        self.positions_ = pd.DataFrame(index=self.stock_data_.index) # 보유 주식 수 데이터프레임
        self.trades_ = pd.DataFrame(columns=['date', 'Type', 'Price', 'Quantity', 'Commission']) # 거래 내역 데이터프레임
        self.portfolio_ = pd.DataFrame(index=self.stock_data_.index) # 포트폴리오 가치 데이터프레임
        self.stats_ = None # 백테스팅 통계 데이터프레임

    # 매수/매도 신호 생성
    def generate_signals(self):
        for i in range(len(self.stock_data_)):
            if self.stock_strategy_.bid_price(i): # 매수 가격이면
                self.signals_.loc[self.stock_data_.index[i], 'signal'] = 1 # 매수 신호 1
            elif self.stock_strategy_.ask_price(i): # 매도 가격이면
                self.signals_.loc[self.stock_data_.index[i], 'signal'] = -1 # 매도 신호 -1
            else: # 그 외에는
                self.signals_.loc[self.stock_data_.index[i], 'signal'] = 0 # 신호 없음 0

    # 매수/매도 신호에 따라 주식 매매 및 포트폴리오 가치 계산
    def execute_trades(self):
        cash = self.initial_capital_ # 현금 잔고
        quantity = 0 # 보유 주식 수
        for i in range(len(self.signals_)):
            date = self.signals_.index[i] # 날짜
            price = self.stock_data_.loc[date, 'close'] # 종가
            signal = self.signals_.loc[date, 'signal'] # 신호

            if signal == 1: # 매수 신호이면
                quantity_to_buy = cash // (price * (1 + self.slippage_)) # 슬리피지 고려하여 구매 가능한 주식 수 계산
                if quantity_to_buy > 0: # 구매 가능한 주식이 있으면
                    commission = quantity_to_buy * price * self.commission_ # 수수료 계산
                    cash -= (quantity_to_buy * price * (1 + self.slippage_) + commission) # 현금 잔고 감소
                    quantity += quantity_to_buy # 보유 주식 수 증가
                    trade = pd.Series([date, 'Buy', price, quantity_to_buy, commission], index=self.trades_.columns) # 거래 내역 생성
                    self.trades_ = self.trades_.append(trade, ignore_index=True) # 거래 내역 추가

            elif signal == -1: # 매도 신호이면
                if quantity > 0: # 보유 주식이 있으면
                    commission = quantity * price * self.commission_ # 수수료 계산
                    cash += (quantity * price * (1 - self.slippage_) - commission) # 현금 잔고 증가
                    quantity = 0 # 보유 주식 수 감소
                    trade = pd.Series([date, 'Sell', price, quantity, commission], index=self.trades_.columns) # 거래 내역 생성
                    self.trades_ = self.trades_.append(trade, ignore_index=True) # 거래 내역 추가

            self.positions_.loc[date, 'quantity'] = quantity # 보유 주식 수 기록
            self.portfolio_.loc[date, 'cash'] = cash # 현금 잔고 기록
            self.portfolio_.loc[date, 'stock'] = quantity * price # 주식 가치 기록
            self.portfolio_.loc[date, 'total'] = cash + quantity * price # 총 포트폴리오 가치 기록

    # 백테스팅 결과 통계적으로 분석
    def analyze_performance(self):
        returns = self.portfolio_['total'].pct_change().fillna(0) # 일별 수익률 계산
        cum_returns = (1 + returns).cumprod() - 1 # 누적 수익률 계산
        annualized_return = cum_returns.iloc[-1] ** (252 / len(returns)) - 1 # 연화 수익률 계산
        annualized_vol = returns.std() * np.sqrt(252) # 연화 변동성 계산
        sharpe_ratio = annualized_return / annualized_vol # 샤프 비율 계산
        max_drawdown = (cum_returns.cummax() - cum_returns).max() # 최대 낙폭 계산
        trade_count = len(self.trades_) // 2 # 거래 횟수 계산
        win_rate = len(self.trades_[self.trades_['Type'] == 'Sell'][self.trades_['Price'] > self.trades_['Price'].shift()]) / trade_count # 승률 계산

        stats = pd.Series([annualized_return, annualized_vol, sharpe_ratio, max_drawdown, trade_count, win_rate],
                          index=['Annualized Return', 'Annualized Volatility', 'Sharpe Ratio', 'Max Drawdown', 'Trade Count', 'Win Rate']) # 통계 데이터프레임 생성
        self.stats_ = stats # 통계 데이터프레임 저장

    # 백테스팅 결과 차트로 시각화
    def plot_performance(self):
        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(16, 12)) # 차트 생성

        self.portfolio_['total'].plot(ax=axes[0], label='Portfolio Value') # 포트폴리오 가치 차트 그리기
        axes[0].set_title('Portfolio Value') # 제목 설정
        axes[0].set_ylabel('Value') # y축 라벨 설정

        buy_signals = self.signals_[self.signals_['signal'] == 1] # 매수 신호 데이터프레임 생성
        sell_signals = self.signals_[self.signals_['signal'] == -1] # 매도 신호 데이터프레임 생성

        self.stock_data_['close'].plot(ax=axes[1], label='Stock Price') # 주식 가격 차트 그리기
        axes[1].plot(buy_signals.index, self.stock_data_.loc[buy_signals.index, 'close'], '^', markersize=10, color='g', label='Buy') # 매수 신호 표시하기
        axes[1].plot(sell_signals.index, self.stock_data_.loc[sell_signals.index, 'close'], 'v', markersize=10, color='r', label='Sell') # 매도 신호 표시하기
        axes[1].set_title('Stock Price and Signals') # 제목 설정
        axes[1].set_ylabel('Price') # y축 라벨 설정

        for ax in axes:
            ax.legend(loc='best') # 범례 표시하기

        plt.show() # 차트 보여주기

    # 백테스팅 실행하기
    def run(self):
        self.generate_signals() # 매수/매도