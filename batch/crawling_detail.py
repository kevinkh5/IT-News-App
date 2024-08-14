from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import execute_values
import asyncio
import ssl
import aiohttp
import certifi
import pytz
import time
from datetime import datetime
pdt_tz = pytz.timezone('America/Los_Angeles')
kst_tz = pytz.timezone('Asia/Seoul')
from pathlib import Path
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
        
# 오늘 날짜를 "YYYY-MM-DD" 형식의 문자열로 변환
today = datetime.now().strftime("%Y-%m-%d")
query = f"SELECT * FROM news_info WHERE DATE(created_at) = '{today}';"

# 쿼리 실행 (필요한 값이 있다면 tuple로 전달)
cursor.execute(query, ('some_value',))

# 결과 가져오기
rows = cursor.fetchall()
# 0 -> id, 5 -> url
url_id_table = {}
all_urls = []
for row in rows:
    query = f"SELECT EXISTS (SELECT 1 FROM news_content WHERE id = {row[0]});"
    cursor.execute(query)
    flag = cursor.fetchone()
    if flag[0]: # 이미 존재하면 continue
        continue
    url_id_table[row[5]] = row[0]
    all_urls.append(row[5])

for urls in all_urls:
    print(urls)

#######################################
############## 비동기 처리
ssl_context = ssl.create_default_context(cafile=certifi.where())

async def fetch(url):
    # async with aiohttp.ClientSession() as session:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        async with session.get(url) as response:
            # 응답 텍스트를 반환
            return await response.text()

async def fetch_all(urls):
    # 모든 요청을 비동기적으로 실행
    tasks = [fetch(url) for url in urls]
    return await asyncio.gather(*tasks)

async def async_process(urls):
    # 모든 URL의 데이터를 비동기적으로 가져옴
    results = await fetch_all(urls)

    # 각 URL의 결과를 출력
    for i, result in enumerate(results):
        soup = BeautifulSoup(result, 'html.parser')
        content_text = soup.find('div', class_='entry-content').text
        result_list.append((urls[i],content_text))

# 제너레이터 함수 정의 : 메모리 효율적으로 배치 처리
def batch_generator(items, batch_size):
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

# 제너레이터를 사용하여 배치 처리 (한번에 5개씩 비동기 처리하고, 5초 쉬기)
batch_size = 5
result_list = []
for batch in batch_generator(all_urls, batch_size):
    print(f"Processing batch: {batch}")
    asyncio.run(async_process(batch))
    time.sleep(5)
    print('len-result_list',len(result_list))
    # 여기에 각 배치에 대한 처리 로직을 추가합니다.

content_info_list = []
for result in result_list:
    url = result[0]
    description = result[1]
    news_info_id = url_id_table[url]
    created_at = datetime.now()
    content_info = (news_info_id, description, created_at)
    content_info_list.append(content_info)

insert_query = """
    INSERT INTO news_content (news_info_id, description, created_at) 
    VALUES %s
    ON CONFLICT (news_info_id) DO NOTHING;
"""
# ON CONFLICT (title) DO NOTHING;는 중복있을시 건너뛰게
# 이거 안쓰면 중복있을시 전체 진행이 안됨

execute_values(cur, insert_query, content_info_list)
# 변경사항을 커밋
conn.commit()

# 커서와 연결을 닫기
if cursor:
    cursor.close()
if conn:
    conn.close()


