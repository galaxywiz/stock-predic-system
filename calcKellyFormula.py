# 백테스팅 클래스의 객체 생성
backtest = Backtest(stock_strategy)

# 매수/매도 신호 생성 및 주식 매매 실행
backtest.run()

# 백테스팅 결과의 통계적 분석 수행
backtest.analyze_performance()

# 백테스팅 승률과 연화 수익률 가져오기
win_rate = backtest.stats_['Win Rate']
annualized_return = backtest.stats_['Annualized Return']

# 켈리 공식에 따라 최적의 배팅 비율 계산
optimal_bet_ratio = win_rate - (1 - win_rate) / annualized_return

# 최적의 배팅 비율 출력
print(f'The optimal bet ratio is {optimal_bet_ratio:.2f}')
