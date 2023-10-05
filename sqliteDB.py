import pandas as pd 
import sqlite3
import os
import traceback

import logger

class SqliteDB:
    def __init__(self, db_name, table_name):
        self.table_struct_ = ""
        self.columns_ = []
        self.init_db(db_name, table_name)

    def init_db(self, db_name, table_name):
        dir = "DB/"
        if os.path.exists(dir) == False:
            os.makedirs(dir)
        self.conn_ = sqlite3.connect(dir + db_name)
        self.db_name_ = db_name
        self.table_name_ = table_name

    def _table_name(self, ticker):
        ticker = ticker.replace("=","_")
        ticker = ticker.replace("/","_")
        ticker = ticker.replace("^","_")
        name = "%s_%s" % (self.table_name_, ticker)
        return name

    #----------------------------------------------------------#
    # 테이블이 있는지 확인하고, 있으면 -1, 없으면 0, 생성했으면 1
    def get_table(self, ticker):
        if self.check_table(ticker) == False:
            if self.create_table(ticker) == False:
                return 0
            else:
                return 1
        return -1

    #----------------------------------------------------------#
    def check_table_and_make(self):
        with self.conn_:
            try:
                cur = self.conn_.cursor()
                sql = "SELECT count(*) FROM sqlite_master WHERE Name = \'%s\'" % self.table_name_
                cur.execute(sql)
                rows = cur.fetchall()
                for row in rows:          
                    if str(row[0]) == "1":
                        return

                cur = self.conn_.cursor()
                sql = "CREATE TABLE %s (%s);" % (self.table_name_, self.table_struct_)
                cur.execute(sql)
            except:
                log = "! [%s] table make fail" % self.table_name_
                logger.error(log)

     # 테이블 이름이 있는지 확인
    def check_table(self, ticker):
        table_name = self._table_name(ticker)
        with self.conn_:
            cur = self.conn_.cursor()
            sql = "SELECT count(*) FROM sqlite_master WHERE Name = \'%s\'" % table_name
            cur.execute(sql)
            rows = cur.fetchall()
            for row in rows:          
                if str(row[0]) == "1":
                    return True
            return False
    
    
   # 테이블 생성
    def create_table(self, ticker):
        table_name = self._table_name(ticker)
        with self.conn_:
            try:
                cur = self.conn_.cursor()
                sql = "CREATE TABLE %s (%s);" % (table_name, self.table_struct_)
                cur.execute(sql)
                return True
            except:
                log = "! [%s] table make fail" % table_name 
                logger.error(log)
                return False
    
    # 데이터 저장
    def save(self, ticker, dataframe):    
        table_name = self._table_name(ticker)
        with self.conn_:
            try:
            #    list_of_rows = dataframe.values.tolist()
                dataframe.to_sql(table_name, self.conn_, if_exists="replace", index = False, dtype={'date': "TIMESTAMP"})
                self.conn_.commit()
            except:
                logger.error(traceback.format_exc())
                return None
            
    # 데이터 로드
    def load(self, ticker, orderBy = "Date ASC", openTime = "", last_limit = 1000):
        table_name = self._table_name(ticker)
        with self.conn_:
            try:  
                columns = ""
                for col in self.columns_:
                    if len(columns) == 0:
                        columns = col
                    else:
                        columns = "%s, %s" % (columns, col)              

                if len(openTime) == 0:
                    sql = "SELECT %s FROM \'%s\' ORDER BY %s" % (columns, table_name, orderBy)
                else:
                    sql = "SELECT %s FROM \'%s\' WHERE Date >= \'%s\' ORDER BY %s" % (columns, table_name, openTime, orderBy)
     
                df = pd.read_sql(sql, self.conn_, index_col=None, parse_dates=['date'])
                length = len(df) 
                if length == 0:
                    return False, None
                
                if length > last_limit:
                    df = df[length - last_limit:]
                
            except:
                logger.error(traceback.format_exc())
                return False, None

        return True, df    

    # 삭제
    def delete(self, ticker):
        table_name = self._table_name(ticker)
        with self.conn_:
            try:  
                cur = self.conn_.cursor()
                sql = "DROP TABLE \'%s\'" % (table_name)
                cur.execute(sql)    
                self.conn_.commit()
            except:
                logger.error(traceback.format_exc())
