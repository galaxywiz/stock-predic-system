#백테스터
from enum import Enum
import pandas as pd 
from pandas import Series, DataFrame
import numpy as np
from datetime import datetime, timedelta

from stockData import StockData, TradingState

class Agent:
    def __init__(self, account):
        # code : sd pair
        self.stocks_ = {}               # 보유 주식
        self.initAccount_ = account     # 초기 자본금
        self.account_ = account         # 현재 자본금

    def haveStock(self, code):
        if code in self.stocks_:
            return True
        return False

    def calcAsset(self):
        total = self.account_
        for code, sd in self.stocks_.items():
            total += sd.calcValue()
        return total

    def calcBuyCount(self, sd):
        nowPrice = sd.nowPrice()
        purchaseAmount = self.account_ / 10

        if self.account_ < purchaseAmount:
            return 0

        count = int(purchaseAmount / nowPrice)
        return count

    def buy(self, sd, timeIdx):
        if self.haveStock(sd.code_):
            return

        buyCount = self.calcBuyCount(sd)
        nowCandle = sd.getCandleAt(timeIdx)
        nowPrice = nowCandle['close']
        self.account_ -= (buyCount * nowPrice)
        
        sd.buyCount_ = buyCount
        sd.buyPrice_ = nowPrice
        sd.buyIdx_ = timeIdx
        self.stocks_[sd.code_] = sd

    def payOff(self, code, timeIdx):
        if self.haveStock(code) == False:
            return

        sd = self.stocks_[code]
        buyCandle = sd.getCandleAt(sd.buyIdx_)
        buyDate = buyCandle['date']

        nowCandle = sd.getCandleAt(timeIdx)
        nowPrice = nowCandle['close']
        sellDate = nowCandle['date']

        value = sd.calcValue(timeIdx = timeIdx)
        self.account_ += value

        haveDay = timeIdx - sd.buyIdx_
        print("[%s] {매수 [%s], [%d] * [%d]} {매도 [%s] [%d]} => 이익[%d], 보유일[%d] => 계좌[%d]" % (sd.name_, buyDate, sd.buyPrice_, sd.buyCount_, sellDate, nowPrice, sd.nowProfit(timeIdx), haveDay, self.account_))
        sd.resetInfo()
        del self.stocks_[code]