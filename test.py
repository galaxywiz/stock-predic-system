# 필요한 모듈 임포트
# requests 모듈과 BeautifulSoup 모듈을 임포트합니다.
import requests
from bs4 import BeautifulSoup

# search_web 함수를 이용하여 웹 검색 결과를 얻습니다.
results = search_web("미국 시가총액 순위")

# 웹 검색 결과 중에서 시가총액 순위를 보여주는 사이트의 URL을 선택합니다.
# 예시로 컴퍼니스마켓캡 사이트의 URL을 선택하였습니다.
url = results["web_search_results"][0]["url"]

# requests 모듈을 이용하여 URL을 요청하고 응답 객체를 저장합니다.
response = requests.get(url)

# BeautifulSoup 모듈을 이용하여 HTML 문서를 파싱합니다.
soup = BeautifulSoup(response.text, "html.parser")

# BeautifulSoup 모듈의 메소드를 이용하여 표나 목록의 태그와 클래스를 찾고, 텍스트 데이터를 추출합니다.
# 예시로 컴퍼니스마켓캡 사이트에서는 <table> 태그와 cmc-table 클래스로 표가 구성되어 있습니다.
table = soup.find("table", class_="cmc-table")
text = table.get_text()

# 추출한 텍스트 데이터에서 티커 정보만을 선택하고, 원하는 개수만큼 잘라냅니다.
# 예시로 상위 50개의 티커만을 가져오려면 리스트 슬라이싱을 이용할 수 있습니다.
tickers = text.split()[3::7] # 티커 정보는 3번째 인덱스부터 7개 간격으로 나타납니다.
top_50 = tickers[:50] # 상위 50개의 티커만을 선택합니다.

# 티커 정보를 출력하거나 반환합니다.
print(top_50)