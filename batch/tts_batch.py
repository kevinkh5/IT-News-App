from dotenv import load_dotenv
import os
from openai import OpenAI
from pathlib import Path
import psycopg2
from datetime import datetime
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
print("download location:",Path(__file__).parent / f"audio/")
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

today = datetime.now().strftime("%Y-%m-%d")
query = f"""
SELECT news_info.id , news_content.description
FROM news_info
INNER JOIN news_content ON news_info.id = news_content.news_info_id
WHERE DATE(news_info.created_at) = '{today}'
"""
cursor.execute(query)
rows = cursor.fetchall()
client = OpenAI()
for row in rows:
    print('news_if_id:',row[0])
    news_if_id = str(row[0])
    file_path = Path(__file__).parent / f"audio/{news_if_id}.mp3"
    if file_path.exists():
        print(f"file already exist! {file_path}")
        continue
    description = row[1]
    if len(description) >= 4096: # 요청할 수 있는 스트링 최대 4096으로, 그 이상이면 스트링 줄이기
        description = description[:4095]
    speech_file_path = Path(__file__).parent / f"audio/{news_if_id}.mp3"
    response = client.audio.speech.create(
          model="tts-1",
          voice="onyx",
          input=description
        )
    response.stream_to_file(speech_file_path)
    print('downloaded!',speech_file_path)

# 커서와 연결을 닫기
if cursor:
    cursor.close()
if conn:
    conn.close()
