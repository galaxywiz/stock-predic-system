# https://xenostudy.tistory.com/505
# pip install telepot
import telepot
from telepot.loop import MessageLoop
import traceback
import requests

import logger

class Messenger:
    def __init__(self, token, id, name):
        self.token_ = token
        self.id_ = id

    def set_market(self, market):
        self.market_ = market

    def send_message(self, message):
        pass

    def send_photo(self, image, message):
        pass

class LineBot(Messenger):
    def send_message(self, message):
        print(message)
        # try:
        #     TARGET_URL = 'https://notify-api.line.me/api/notify' 
        #     headers={'Authorization': 'Bearer ' + self.token_}  
        #     data={'message': message}
        #     response = requests.post(TARGET_URL, headers=headers, data=data)

        # except Exception as ex:
        #     logger.error(traceback.format_exc())

    def send_photo(self, image_path, message):
        print(message)
        # try:
        #     TARGET_URL = 'https://notify-api.line.me/api/notify' 
        #     headers={'Authorization': 'Bearer ' + self.token_}  
        #     data={'message': message}
        #     file = {'imageFile':open(image_path, 'rb')}
        #     response = requests.post(TARGET_URL, headers=headers, files=file, data=data)

        # except Exception as ex:
        #     logger.error(traceback.format_exc())

class TelegramBot(Messenger):
    def __init__(self, token, id, name):
        super().__init__(token, id, name)

  #      self.messenger_bot_ = telepot.Bot(self.token_)
  #      self.recvmsg_handler_reg(self.on_chat_message)
  #      self.send_message("파이썬 " + name + " 서비스 시작")

    def recvmsg_handler_reg(self, func):
 #       self.messenger_bot_.setWebhook()
   #     MessageLoop(self.messenger_bot_, func).run_as_thread()
        pass

    def send_message(self, message):
        print(message)
        # try:
        #     self.messenger_bot_.sendMessage(self.id_, message)
        # except:
        #     logger.error(traceback.format_exc())

    def send_photo(self, image, message):
        print(message)
        # try:
        #     self.messenger_bot_.sendPhoto(
        #         self.id_, photo=open(image, 'rb'), caption=message)
        # except:
        #     logger.error(traceback.format_exc())

    #------------------------------------------------------------------#
    # 메시지 분석 해서 리턴
    def on_chat_message(self, msg):
        # 입력받은 메세지에 대한 정보들을 각각 저장.
        content_type, chat_type, chat_id = telepot.glance(msg)
        # print('Chat Message:', content_type, chat_type, chat_id) # 메세지에 대한 정보들을 console 창에 print
        try:
            if content_type == 'text':
                text = msg["text"]
                if text[0] == '/':
                    self.on_command(text)
                else:
                    help_message = "* 지원되는 명령어. \n"
                    help_message += "/예측 [티거]\n"
                    help_message += "/그래프 [티거]\n"
                    help_message += "/가격 [티거]\n"
                    help_message += "/목록\n"
                    help_message += "/매수리스트\n"
                    help_message += "/매도리스트\n"

                    self.send_message(help_message)
        except:
            logger.error(traceback.format_exc())

    def _get_stock_data(self, ticker):
        sd = self.market_.get_stock(ticker)
        if sd == None:
            sd = self.market_.get_stock_ticker(ticker)
            if sd == None:
                self.send_message("티거 or 주식 이름이 잘못 되거나 없음 [%s]" % command)
                return None
        return sd

    def on_command(self, command):
        cmd_list = command.split(' ')
        if len(cmd_list) < 1:
            self.send_message("명령어가 잘못 입력됨. [%s]" % command)
            return

        cmd = cmd_list[0]

        if cmd == "/예측" or cmd == "/list":
            self._command_predic(cmd_list[1])
            return

        if cmd == "/그래프" or cmd == "/graph":
            self._command_graph(cmd_list[1])
            return

        if cmd == "/가격" or cmd == "/전략" or cmd == "/price":
            self._command_strategy(cmd_list[1])
            return

        if cmd == "/목록" or cmd == "/리스트" or cmd == "/list":
            self._command_get_list()
            return

        if cmd == "/매수리스트" or cmd == "/매수추천" or cmd == "/listbuy":
            self._command_recommand_buy_list()
            return

        if cmd == "/매도리스트" or cmd == "/매도추천" or cmd == "/listsell":
            self._command_recommand_sell_list()
            return

    # --------------------------------------------------------
    def _command_predic(self, ticker):
        sd = self._get_stock_data(ticker)
        if sd == None:
            self.send_message("%s 를 찾을 수 없습니다" % ticker)
            return

        if sd.predic_price_ == None:
            sd.predic_price_ = 0
        msg = "= %s 의 현재[%.2f], 예측은 [%.2f]" % (
            sd.name_, sd.now_price(), sd.predic_price_)
        self.send_message(msg)

    def _command_graph(self, ticker):
        sd = self._get_stock_data(ticker)
        if sd == None:
            self.send_message("%s 를 찾을 수 없습니다" % ticker)
            return

        if sd.predic_price_ == None:
            sd.predic_price_ = 0
        msg = "= %s 의 현재[%.2f], 예측은 [%.2f]" % (
            sd.name_, sd.now_price(), sd.predic_price_)
        self.market_.send_chart_log(sd.name_, msg)

    def _command_strategy(self, ticker):
        sd = self._get_stock_data(ticker)
        if sd == None:
            self.send_message("%s 를 찾을 수 없습니다" % ticker)
            return

        strategy = sd.get_strategy()
        if strategy == None:
            strategy = self.market_.config_.strategy_

        name = strategy.__class__.__name__
        msg = "= %s 의 현재[%.2f], 전략 [%s]" % (sd.name_, sd.now_price(), name)
        self.send_message(msg)

    def _command_get_list(self):
        title = msg = "= 이름, 티거, lastDate, 종가, 예측종가, 전략\n"
        count = 0
        for sd in self.market_.stock_pool_.values():
            strategy = sd.get_strategy()
            if strategy == None:
                strategy = self.market_.config_.strategy_

            name = strategy.__class__.__name__
            name = name.replace("TradeStrategy", "")
            if sd.predic_price_ == None:
                sd.predic_price_ = 0
            msg += "%s, %s, %s, %.2f, %.2f, %s\n" % (
                sd.name_, sd.ticker_, sd.now_candle_time(), sd.now_price(), sd.predic_price_, name)
            count += 1

            if count >= 50:
                self.send_message(msg)
                count = 0
                msg = title

        self.send_message(msg)

    def _command_recommand_buy_list(self):
        title = msg = "### ↑ 종가 < 예측 : 매수 추천\n= 이름, 티거, lastDate, 종가, 예측종가, 차이, 전략\n"
        count = 0

        for sd in self.market_.stock_pool_.values():
            strategy = sd.get_strategy()
            if strategy == None:
                strategy = self.market_.config_.strategy_

            name = strategy.__class__.__name__
            name = name.replace("TradeStrategy", "")
            if sd.predic_price_ == None:
                continue

            if sd.predic_price_ > sd.now_price():
                msg += "%s, %s, %s, %.2f, %.2f, %.2f%%, %s\n" % (sd.name_, sd.ticker_, sd.now_candle_time(
                ), sd.now_price(), sd.predic_price_, sd.predic_difference_rate()*100, name)
                count += 1

            if count >= 50:
                self.send_message(msg)
                count = 0
                msg = title

        self.send_message(msg)

    def _command_recommand_sell_list(self):
        title = msg = "### ↓ 예측 < 종가 : 매도 추천\n= 이름, 티거, lastDate, 종가, 예측종가, 차이, 전략\n"
        count = 0

        for sd in self.market_.stock_pool_.values():
            strategy = sd.get_strategy()
            if strategy == None:
                strategy = self.market_.config_.strategy_

            name = strategy.__class__.__name__
            name = name.replace("TradeStrategy", "")
            if sd.predic_price_ == None:
                continue

            if sd.predic_price_ < sd.now_price():
                msg += "%s, %s, %s, %.2f, %.2f, %.2f%%, %s\n" % (sd.name_, sd.ticker_, sd.now_candle_time(
                ), sd.now_price(), sd.predic_price_, sd.predic_difference_rate()*100, name)
                count += 1

            if count >= 50:
                self.send_message(msg)
                count = 0
                msg = title

        self.send_message(msg)
