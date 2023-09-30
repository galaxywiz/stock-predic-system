from sqliteDB import SqliteDB

class DayPriceDB(SqliteDB):
    def init_db(self, db_name, table_name):
        super().init_db(db_name, table_name)

        self.table_struct_ = "Date DATETIME PRIMARY KEY, Open INTEGER, High INTEGER, Low INTEGER, Close INTEGER, Volume INTEGER"
        self.columns_ = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

class DayPriceFloatDB(SqliteDB):
    def init_db(self, db_name, table_name):
        super().init_db(db_name, table_name)

        self.table_struct_ = "Date DATETIME PRIMARY KEY, Open FLOAT, High FLOAT, Low FLOAT, Close FLOAT, Volume INTEGER"
        self.columns_ = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

#----------------------------------------------------------#
# 행복의 도구에서 사용할 주식 목록
class DayPreDB(SqliteDB):
    def init_db(self, db_name, table_name = "TODAY_STOCK_LIST"):
        super().init_db(db_name, table_name)

        self.table_struct_ = "Name TEXT, Ticker TEXT, Date DATETIME, strategyAction TEXT, ClosePrice INT, Volume INT"
        self.columns_ = ['Name', 'Ticker', 'Date', 'strategyAction', 'ClosePrice', 'Volume']
        self.check_table_and_make()
        
    def save_stock_data(self, stock_pool):        
        with self.conn_:
            #try:
                for name, sd in stock_pool.items():
                    cur = self.conn_.cursor()
                    columns = ""
                    for col in self.columns_:
                        if len(columns) == 0:
                            columns = "'%s'" % (col)
                        else:
                            columns = "%s, '%s'" % (columns, col)
                    
                    now_candle = sd.candle0()
                    dateTime = now_candle['Date']
                    price = now_candle['close']
                    vol = now_candle['vol']

                    dateTime = dateTime.replace('.', '-')
                    changeName = name.replace('\'','')
                    sql = "DELETE FROM \'%s\' WHERE code = '%s' and Date = '%s'" % (self.table_name_, sd.ticker_, dateTime)
                    cur.execute(sql)    

                    value = "'%s', '%s', '%s', '%s', %d, %d" % (changeName, sd.ticker_, dateTime, sd.strategy_action_.name, price, vol)
                    sql = "INSERT INTO \'%s\' (%s) VALUES(%s)" % (self.table_name_, columns, value)
                    cur.execute(sql)    
                    self.conn_.commit()
            #except:
             #   return None
#----------------------------------------------------------#
class PredictionDB(SqliteDB):
    def init_db(self, db_name, table_name):
        super().init_db(db_name, table_name)    
    
class PredicDB(PredictionDB):
    def init_db(self, db_name, table_name):
        super().init_db(db_name, table_name)
        
        self.table_struct_ = "Date DATETIME PRIMARY KEY, Open INT, High INT, Low INT, Close INT, Vol INT, Predic Float, StrategyAction INT"
        self.columns_ = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Predic', 'StrategyAction']

    # 데이터 저장
    def save_stock_data(self, sd):    
        table_name = super()._table_name(sd.ticker_)
        candle = sd.candle0()
        dateTime = candle["Date"] ## 예측값은 이 값의 다음날임.
        #now = time.localtime()
        #dateTime = "%04d.%02d.%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        with self.conn_:
            try:
                cur = self.conn_.cursor()
                columns = ""
                for col in self.columns_:
                    if len(columns) == 0:
                        columns = col
                    else:
                        columns = "%s, '%s'" % (columns, col)

                open = candle["Open"]
                high = candle["High"]
                low = candle["Low"]
                close = candle["Close"]
                vol = candle["Volume"]
                value = "'%s', %d, %d, %d, %d, %d, %2.2f, %d" % (dateTime, open, high, low, close, vol, sd.predicPrice_, sd.strategyAction_.value)
                sql = "INSERT OR REPLACE INTO \'%s\' (%s) VALUES(%s)" % (table_name, columns, value)
                cur.execute(sql)    
                self.conn_.commit()
            except:
                return None


class PredicFloatDB(PredictionDB):
    def init_db(self, db_name, table_name):
        super().init_db(db_name, table_name)
        
        self.table_struct_ = "Date DATETIME PRIMARY KEY, Open Float, High Float, Low Float, Close Float, Volume INT, Predic Float, StrategyAction INT"
        self.columns_ = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Predic', 'StrategyAction']
        
    # 데이터 저장
    def save_stock_data(self, sd):    
        table_name = super()._table_name(sd.ticker_)
        candle = sd.candle0()
        dateTime = candle["Date"] ## 예측값은 이 값의 다음날임.
        #now = time.localtime()
        #dateTime = "%04d.%02d.%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        with self.conn_:
           # try:
                cur = self.conn_.cursor()
                columns = ""
                for col in self.columns_:
                    if len(columns) == 0:
                        columns = col
                    else:
                        columns = "%s, '%s'" % (columns, col)

                open = candle["Open"]
                high = candle["High"]
                low = candle["Low"]
                close = candle["Close"]
                vol = candle["Volume"]
                value = "'%s', %2.2f, %2.2f, %2.2f, %2.2f, %d, %2.2f, %d" % (dateTime, open, high, low, close, vol, sd.predicPrice_, sd.strategyAction_.value)
                sql = "INSERT OR REPLACE INTO \'%s\' (%s) VALUES(%s)" % (table_name, columns, value)
                cur.execute(sql)    
                self.conn_.commit()
            #except:
                return None
