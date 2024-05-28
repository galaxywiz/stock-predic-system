import requests
from bs4 import BeautifulSoup

# 네이버 금융 사이트 URL
url = 'https://finance.naver.com/sise/item_gold.naver'

# 웹 페이지 가져오기
response = requests.get(url)
response.encoding = 'euc-kr'  # 한글 인코딩 설정
html = response.text

# BeautifulSoup으로 HTML 파싱
soup = BeautifulSoup(html, 'html.parser')
# 종목명을 저장할 리스트
stock_names = {}
ticker = []
sname = []

items = soup.find_all('a', class_='tltle')
for item in items:
    code = item['href'].split('=')[-1]
    name = item.get_text()
    ticker.append(code)
    sname.append(name)    

stock_names['ticker'] = ticker
stock_names['name'] = sname

for ticker, name in stock_names.items():
    print("{0} ticker = {1}".format(ticker, name))

# import yfinance as yf
# import pandas as pd
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch

# # 주식 데이터 가져오기
# def fetch_stock_data(ticker, period='1mo', interval='1d'):
#     stock = yf.Ticker(ticker)
#     data = stock.history(period=period, interval=interval)
#     return data

# # LLaMA 모델을 사용하여 분석하기
# def analyze_stock_with_llama(stock_data):
#     # LLaMA 모델 로드
#     model_name = "stockmark/stockmark-100b"
#     tokenizer = AutoTokenizer.from_pretrained(model_name)
#     model = AutoModelForCausalLM.from_pretrained(model_name)

#     # 주식 데이터를 문자열로 변환
#     data_str = stock_data.to_string()

#     # 입력 데이터 준비
#     inputs = tokenizer(data_str, return_tensors="pt", truncation=True, max_length=512)
#     input_ids = inputs["input_ids"]

#     # 모델에 입력 데이터 전달 및 출력 생성
#     with torch.no_grad():
#         outputs = model.generate(input_ids, max_length=1024)

#     # 결과 해석
#     analysis = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return analysis

# # 주식 티커와 분석 기간 설정
# ticker = "AAPL"
# period = "1mo"
# interval = "1d"

# # 주식 데이터 가져오기
# stock_data = fetch_stock_data(ticker, period, interval)
# print("Stock Data:\n", stock_data)

# # LLaMA 모델로 분석
# analysis = analyze_stock_with_llama(stock_data)
# print("\nStock Analysis:\n", analysis)

# from ultralyticsplus import YOLO, render_result
# import cv2

# # load model
# model = YOLO('foduucom/stockmarket-future-prediction')

# # set model parameters
# model.overrides['conf'] = 0.25  # NMS confidence threshold
# model.overrides['iou'] = 0.45  # NMS IoU threshold
# model.overrides['agnostic_nms'] = False  # NMS class-agnostic
# model.overrides['max_det'] = 1000  # maximum number of detections per image

# # set image
# image = './chart/USA/five/Tesla.png'

# # perform inference
# results = model.predict(image)

# # observe results
# print(results[0].boxes)
# render = render_result(model=model, image=image, result=results[0])
# render.show()

#----------------------------------------------------------------------
# #https://lsjsj92.tistory.com/666 참고
# import ollama

# respone = ollama.chat(model='llama3', 
#                       messages=[
#                           {'role' : 'user', 
#                            'content' : '올해의 테슬라 주가 전망을 해줘.'
#                            },
#                       ])

# print(respone['message']['content'])

#----------------------------------------------------------------------
# import openai
# import time

# # Replace 'your-api-key' with your actual OpenAI API key
# openai.api_key = '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'

# def ask_chatgpt(question):
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": question}
#             ]
#         )
#         answer = response['choices'][0]['message']['content'].strip()
#         return answer
#     except openai.error.RateLimitError:
#         print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
#         time.sleep(60)  # Wait for a minute before retrying
#         return ask_chatgpt(question)  # Retry the request

# if __name__ == "__main__":
#     question = "2024년 5월달 테슬라 주식을 보고, 5월 24일의 테슬라 주식을 분석해줘"
#     answer = ask_chatgpt(question)
#     print("ChatGPT's answer:")
#     print(answer)



# from openai import OpenAI  

# client = OpenAI(  
#                   base_url = "http://sionic.chat:8001/v1",     
#                   api_key = "934c4bbc-c384-4bea-af82-1450d7f8128d" )  

# response = client.chat.completions.create(     
#             model="xionic-ko-llama-3-70b",     
#             messages=[         
#                 {"role": "system", "content": "You are an AI assistant. You will be given a task. You must generate a detailed and long answer in korean."},
#                 {"role": "user", "content": "이번달 테슬라 주식 분석과, 다음달 테슬라 주식 예측을 해줘"}
#                 ] 
#         )
  
# print (response.choices[0].message.content) 