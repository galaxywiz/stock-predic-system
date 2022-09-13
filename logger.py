#logging warper
import logging
import logging.handlers

loggerModule = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')
stramHandler = logging.StreamHandler()
fileHandler = logging.FileHandler('./log.csv', encoding='UTF-8')

stramHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)

loggerModule.addHandler(stramHandler)
loggerModule.addHandler(fileHandler)

def debug(string):
    loggerModule.setLevel(level=logging.DEBUG)
    loggerModule.debug(string)

def info(string):
    loggerModule.setLevel(level=logging.INFO)
    loggerModule.info(string)

def error(string):
    loggerModule.setLevel(level=logging.ERROR)
    loggerModule.error(string)
