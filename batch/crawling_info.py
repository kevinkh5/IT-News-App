import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import pytz
pdt_tz = pytz.timezone('America/Los_Angeles')
kst_tz = pytz.timezone('Asia/Seoul')
from pathlib import Path
import time
dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path)
# 데이터베이스 연결 정보
conn_params = {
    'dbname': os.getenv('dbname'),
    'user': os.getenv('user'),
    'password': os.getenv('password'),
    'host': os.getenv('host'),
    'port': os.getenv('port')
}

# 데이터베이스에 연결
cnt = 5
for i in range(cnt):
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        cur = conn.cursor()
        print("Database connection successful")
        break
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        if i < cnt-1:
            time.sleep(10)
            continue
        exit()

# 크롤링할 웹 페이지의 URL
urls = ['https://techcrunch.com/category/apps/',
        'https://techcrunch.com/category/artificial-intelligence/']

for url in urls:
    # 웹 페이지 요청
    response = requests.get(url)
    # 페이지의 HTML을 파싱하기 위해 BeautifulSoup 객체 생성
    soup = BeautifulSoup(response.text, 'html.parser')
    # 기사 뭉치 리스트
    article_list = soup.find_all('div', class_='wp-block-tc23-post-picker')

    article_info_list = []
    for article in article_list:
        try:
            category = article.find('a').text.strip()
            category = category[:30]
            title = article.find('h2').text
            author = article.find('div', class_="is-style-default wp-block-tc23-author-card").text.strip()
            img_link = article.find('figure').find('img').attrs['src']
            destination_link = article.find('h2').find('a').attrs['data-destinationlink']
            date = article.find('time').attrs['datetime']
            # date타입 & PDT -> KST 변환
            try:
                date1 = datetime.fromisoformat(date)
                date2 = date1.strftime("%Y-%m-%dT%H:%M:%S")
                pdt_time = datetime.strptime(date2, '%Y-%m-%dT%H:%M:%S')
                pdt_time = pdt_tz.localize(pdt_time)
                kst_time = pdt_time.astimezone(kst_tz)
                date = kst_time
            except:
                date = None
            created_at = datetime.now()
            article_info = (category, title, author, img_link, destination_link, date, created_at)
            print(article_info)
            article_info_list.append(article_info)
        except Exception as e:
            print('Crawling Failed')
            print(e)
            continue

    # for a in article_info_list:
    #     print(a)
    print("total : ",len(article_info_list))
    ############# Example Data
    # article_info_list = [('AI', 'Rabbit’s r1 refines chats and timers, but its app-using ‘action model’ is still MIA',
    # 'Devin Coldewey', 'https://techcrunch.com/wp-content/uploads/2024/08/rabbit-timers.jpg?w=430',
    # 'https://techcrunch.com/2024/08/08/rabbits-r1-refines-chats-and-timers-but-its-app-using-action-model-is-still-mia/',
    # datetime.datetime(2024, 8, 8, 13, 29, 41, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=61200))),
    # datetime.datetime(2024, 8, 9, 10, 58, 40, 802405))]
    #############
    insert_query = """
        INSERT INTO news_info (category, title, author, img_link, destination_link, date, created_at) 
        VALUES %s
        ON CONFLICT (title) DO NOTHING;
    """
    # ON CONFLICT () DO NOTHING;는 중복있을시 건너뛰게

    execute_values(cur, insert_query, article_info_list[:3]) # 3개씩만 DB에 가져오기
    # 변경사항을 커밋
    conn.commit()


# 커서와 연결을 닫음
cur.close()
conn.close()
