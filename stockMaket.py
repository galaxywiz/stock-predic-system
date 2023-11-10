#주식 차트 실습
#https://chancoding.tistory.com/117?category=846070
from datetime import datetime
from datetime import timedelta
import os
import shutil
import glob
import locale
import logger

from stockData import StockData
from stockDo import PredicStockDo, StrategyStockDo

class StockMarket:
    REFRESH_DAY = 1
    MAX_WATHCING_STOCK = 200        # 최대 거래 체크
    TOP_VOL_RATE_STOCK = 0.25       # 전체 주식중 거랴량 상위 %만 매매

    def __init__(self, market_config, real_trade=False):
        self.stock_pool_ = {}
        self.stock_strategy_ = {}
        self.time_line_ = datetime.now().strftime("%Y-%m-%d")
        self.config_ = market_config
        self.name_ = self.config_.name_
        
        self.messenger_ = self.config_.messenger_
        self.DATE_FMT = market_config.DATE_FMT
        self.chart_dir_ = ("./chart/%s" % self.name_)

        locale.setlocale(locale.LC_ALL, '')
        now = datetime.now() - timedelta(days=1)  
        self.last_crawling_time_ = now
 
        self.get_stocks_list()
        
        # msg = "%s is ready" % (self.name_)
        # self.send_message(msg)

    def __process(self):
        self.update_stocks()
        self.predic_stock()

    def do(self):
        if self.config_.crawling_time():
            now = datetime.now()
            elpe = now - self.last_crawling_time_
            if elpe.total_seconds() < (60*60):  # 1시간 마다 체크
                return

            logger.info("### [%s] market run. check [%d] stocks" % (self.name_, len(self.stock_pool_)))
            self.last_crawling_time_ = now
            self.__process()
            self.copy_db()
            logger.info("### [%s] market job completed." % self.name_)

    #----------------------------------------------------------#
    # 메시지 전송용
    def send_message(self, log):
        self.messenger_.send_message(log)
    
    def send_chart_log(self, log, chart_path):
        if chart_path == None or len(chart_path) == 0:
            self.messenger_.send_message(log)
        else:
            self.messenger_.send_photo(log, chart_path)

    #----------------------------------------------------------#
    # db 에 데이터 저장 하고 로딩!
    def __get_stock_info_from_web_to_db(self, name, ticker):
        load_days = 365 * 10  #10 년치
        
        df = self.config_.crawler_.get_stock_data(ticker, load_days)
        if df is None:
            logger.error("! 주식 [%s] 의 크롤링 실패" % (name))
            return None

        return df
        
    def __check_db_exist(self, ticker):
        db = self.config_.day_price_db_
        
        ret = db.check_table(ticker)
        if ret == False:
            return False
        return True
    
    def __load_from_db(self, ticker):
        db = self.config_.day_price_db_
        
        ret, df = db.load(ticker)
        if ret == False:
            return False, None

        return True, df

    def __check_data_frame(self, df, name, ticker):
        LIMIT_DAY = 100
        #30일전 데이터가 있는지 체크
        if len(df) < LIMIT_DAY:
            logger.error("[%s][%s] load fail. because data too short" % (name, ticker))
            return False

        prev_date_str = df.iloc[-15]['date']
        candle_date = prev_date_str #datetime.strptime(prev_date_str, self.DATE_FMT)
        now = datetime.now()

        elpe = (now - candle_date).days
        if elpe > LIMIT_DAY:
            logger.error("%s 데이터 로딩 실패, db 에서 데이터 삭제" % name)
            self.config_.day_price_db_.delete(ticker)
            return False
        
        return True
        
    ## 주식 데이터 로딩 ##
    def __load_stock_data(self, name, ticker, market_cap_ranking, having):  
        # 일단 web에서 데이터 조회 및 저장
        df = self.__get_stock_info_from_web_to_db(name, ticker)
        if df is None:
            return
        
        # 데이터 저장    
        db = self.config_.day_price_db_
        db.save(ticker, df)

        # db 저장했다가 로딩하는 처리 block. 굳이...day 하는데 필요한가 싶음.
        USE_DB = False
        if USE_DB:
            if self.__check_db_exist(ticker) == False:
                logger.error("[%s][%s] load fail from web." % (name, ticker))
                return None             
            
            ret, df = self.__load_from_db(ticker)
            if ret == False:
                logger.error("[%s][%s] load fail. from db" % (name, ticker))
                return None

        if self.__check_data_frame(df, name, ticker) is False:
            return

        sd = StockData(ticker, name, df)
        self.stock_pool_[name] = sd
        sd.calc_indicator()
        sd.set_candle_fmt(self.DATE_FMT)
        sd.set_type(self.config_.stock_type_)
        sd.market_cap_ranking_ = int(market_cap_ranking)
        sd.having_ = int(having)

        logger.info("[%s] data 로딩완료. last date [%s]" % (sd.name_, sd.now_candle_time()))
        print(df)

    def get_stocks_list(self, limit = -1):
        self.stock_pool_.clear()
        is_file_load = self.config_.is_file_load_
        if is_file_load:
            file_name = self.config_.list_file_name_
            stock_df = self.config_.crawler_.get_stocks_list_from_file(file_name)
        else: 
            table_limit = self.config_.limit_list_size_
            is_debug = self.config_.is_debug_
            stock_df = self.config_.crawler_.get_stock_list(table_limit, debug=is_debug) 
            
        # 주식의 일자데이터 크롤링 / db 에서 갖고 오기
        for idxi, row in stock_df.iterrows():
            name = row['name']
            ticker = row['ticker']
            market_cap_ranking = row['ranking']
            having = row['having']

            if type(name) != str:
                continue
            self.__load_stock_data(name, ticker, market_cap_ranking, having)
            logger.info("[%s] ticker[%s] loading complet" %(name, ticker))
            if limit > 0:
                if idxi > limit:
                    break

    def __check_now_time(self, sd):
        if self.config_.is_debug_:
            return True

        now = datetime.now()
        now_candle = sd.candle0()
        date_str = now_candle['date']
        candle_date = datetime.strptime(date_str, self.DATE_FMT)
        elpe = (now - candle_date).days
        
        temp = self.REFRESH_DAY
        if now.weekday() == 6:
            temp = temp + 2

        if elpe <= temp:
            return True
        return False

    def update_agent_balance(self):
        for agent in self.agents_:
            agent.update_balance()
            agent.update_have_stocks()

    def print_agent_balance(self):
        for agent in self.agents_:
            agent.print_balance_evaluation()

    def update_stocks(self):
        # 거래량 많은순으로 본다
        vol_desc = self._vol_desc_stocks()        

        # 데이터 얻어 오고 거래 시도를 한다.
        for ticker in vol_desc:
            if ticker not in self.stock_pool_:
                continue
            sd = self.stock_pool_[ticker]

            name = sd.name_
            ticker = sd.ticker_
            market_cap = 0
            self.__load_stock_data(name, ticker, market_cap)

    def get_stock(self, name):
        if name in self.stock_pool_:
            return self.stock_pool_[name]
        return None
    
    def get_stock_ticker(self, ticker):
        for sd in self.stock_pool_.values():
            if sd.ticker_ == ticker:
                return sd

        return None   
        
    #----------------------------------------------------------#
    # 예측 봇을 돌리는 용도
    def predic_stock(self):
        predic = PredicStockDo(self)
        predic.do()
        # # s&p 500 지수를 같이 참고로 예측
        # if self.config_.index_ticker_ not in self.stock_pool_:
        #     logger.info("s&p 지수 로딩 실패")
        #     return
        
        # stock_price_index = self.stock_pool_[self.config_.index_ticker_]

        # recommand_buy = {}
        # recommand_sell = {}
        # for sd in self.stock_pool_.values():
        #     model_name = self.config_.name + '_' + sd.name_
        #     mm_predic = sp.StockPredic(sd, stock_price_index, model_name)
        #     predic = mm_predic.predic()   
        #     sd.predic_price_ = predic

        #     predic_price = predic[0]
        #     chart_file = PrintChart.saveFigure(self.chart_dir_, sd, self.DATE_FMT)

        #     now_date = sd.now_candle_time()
        #     now_price = sd.now_price()
        #     if now_price < predic_price:
        #         recommand_buy[sd.name_] = [now_date, now_price, predic_price, chart_file]
        #     else:
        #         recommand_sell[sd.name_] = [now_date, now_price, predic_price, chart_file]

        # log = "### 상승 예감 ↑ 매수 추천\n"
        # for name, data in recommand_buy.items():
        #     l = ("[%s]의 [%s]의 종가[%2.2f], 다음 예측[%2.2f], 상승률[%2.2f]\n" %
        #             (name, data[0], data[1], data[2], u.calcRate(data[1], data[2])*100))
        #     self.send_chart_log(l, data[3])
        #     log += l

        # log = "### 하락 예감 ↓ 매도 추천 "
        # for name, data in recommand_sell.items():
        #     l = ("[%s]의 [%s]의 종가[%2.2f], 다음 예측[%2.2f], 하락률[%2.2f]\n" %
        #             (name, data[0], data[1], data[2], u.calcRate(data[1], data[2])*100))
        #     self.send_chart_log(l, data[3])
        #     log += l

        # self.send_message(log)

    #----------------------------------------------------------#
    def check_strategy(self):
        strategy = StrategyStockDo(self)
        strategy.do()
        
    #----------------------------------------------------------#
    # 거래량 많은 순서대로 의미 있는 수급량만 거래
    def _vol_desc_stocks(self):
        list_stocks = {}
        for name, sd in self.stock_pool_.items():
            list_stocks[name] = sd.now_vol()

        desc_list = sorted(list_stocks.items(), key=lambda x: x[1], reverse=True)
        name_list = []
        for name, vol in desc_list:
            name_list.append(name)

        size = len(name_list)
        limit = int(size * self.TOP_VOL_RATE_STOCK) 
        limit = max(limit, self.MAX_WATHCING_STOCK)
        name_list = name_list[:limit]
        return name_list

    def _check_pay_off(self, agent, ticker):
        if ticker not in self.stock_pool_:
            logger.error("%s ticker is not market" % ticker)
            return

        sd = self.stock_pool_[ticker]
        st = agent.get_stock_statement(ticker)
        if st == None:
            logger.error("%s ticker agent not have" % ticker)
            return

        sd.buy_time_ = st.buy_time_
        logger.info("* %s payoff check, buy time %s" % (sd.name_, sd.buy_time_))
        
        if agent.have_stock(ticker):
            amount = st.buy_amount_
            if amount > 0:
                agent.pay_off(ticker, amount)

    def _check_buy(self, agent, ticker):
        sd = self.stock_pool_[ticker]
        if self.__check_now_time(sd) == False:
            return
        
        if agent.have_stock(ticker):
            return

        # 매수 신호 확인
        if agent.buy(ticker):
            logger.info("* %s buy, buy time %s" % (sd.name_, sd.buy_time_))
       
    def trade(self, agent, ticker):
        if ticker in self.stock_strategy_:
            strategy = self.stock_strategy_[ticker]
            if strategy != False:
                sd = self.stock_pool_[ticker]
                sd.set_strategy(strategy)

        # 매수한것부터 먼저 매도 체크
        if agent.have_stock(ticker):
            self._check_pay_off(agent, ticker)
            return

        # 매수 체크
        self._check_buy(agent, ticker)

    #-----------------------------------------------
    # 테스트 용도의 trade 직접 써도 되지만, 지금은 안씀
    def do_trade(self):
        for agent in self.agents_:
            agent.update_balance()
            agent.update_have_stocks()

            have_stock = list(agent.have_stocks().keys()).copy()
            # 매수한것부터 먼저 매도 체크
            for ticker in have_stock:
                self._check_pay_off(agent, ticker)

            # 매수 체크
            vol_desc = self._vol_desc_stocks()
            for ticker in vol_desc:
                self._check_buy(agent, ticker)

            agent.print_balance_evaluation()

        for agent in self.agents_:
            agent_name = agent.__class__.__name__
            logger.info("[%s]의 현재 btc = [%f]" % (agent_name, agent.calc_balance_evaluation()))
   
    def wathing_and_trade(self):
        # 거래량 많은순으로 본다
        vol_desc = self._vol_desc_stocks()        
        self.update_agent_balance()

        # 데이터 얻어 오고 거래 시도를 한다.
        for ticker in vol_desc:
            if ticker not in self.stock_pool_:
                continue
            sd = self.stock_pool_[ticker]

            name = sd.name_
            ticker = sd.ticker_
            market_cap = 0
            self.__load_stock_data(name, ticker, market_cap)
            
            for agent in self.agents_:
                code = sd.get_ticker()
                self.trade(agent, code)

        self.print_agent_balance()

        # 다 했으면, 혹시 전략이 비는 애들은 다시 맞춰준다(최초 1회)
        for ticker in vol_desc:
            if ticker not in self.stock_pool_:
                continue
            sd = self.stock_pool_[ticker]
            
            if sd.get_strategy() == None:
                if ticker in self.stock_strategy_:
                    if self.stock_strategy_[ticker] == False:
                        continue

                strategy, profit = self.find_good_strategy(sd)
                if strategy != None:
                    sd.set_strategy(strategy)
                    self.stock_strategy_[ticker] = strategy
                    logger.info("%s 전략 = %s" % (sd.name_, strategy.__class__.__name__))
                else:
                    self.stock_strategy_[ticker] = False
                    logger.info("%s 적절한 전략 없음" % (sd.name_))

    #----------------------------------------------------------#
    def copy_db(self):
        backup_path = os.getcwd() + "/DB_Backup/"
        if os.path.exists(backup_path) == False:
            os.makedirs(backup_path)

        for file_name in glob.glob(os.path.join(os.getcwd() + "/DB/", '*.*')):
            shutil.copy(file_name, backup_path)
        #logger.info("DB 파일 복사 완료")
    
    #----------------------------------------------------------#
