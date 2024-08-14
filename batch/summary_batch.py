from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from openai import OpenAI
import psycopg2
from dotenv import load_dotenv
import os
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
SELECT news_content.news_info_id , news_content.description
FROM news_content
WHERE summary IS NULL AND DATE(created_at) = '{today}'
"""

cursor.execute(query)
rows = cursor.fetchall()
client = OpenAI()
model = ChatOpenAI(model="gpt-4-1106-preview", temperature=1.0)

class Summary(BaseModel):
    summary: str = Field(description="이해하기 쉽고 간결하게 요약하라. 5문장 이내의 영어로.")

for row in rows:
    news_info_id = row[0]
    description = row[1]
    if len(description) >= 4096: # 요청할 수 있는 스트링 최대 4096으로, 그 이상이면 스트링 줄이기
        description = description[:4095]
    parser = JsonOutputParser(pydantic_object=Summary) # JsonOutputParser는 JSON 형태의 출력을 파싱하는 도구
    format_instruction = parser.get_format_instructions() # Summary 모델에 맞는 출력 포맷에 대한 지침
    human_msg_prompt_template = HumanMessagePromptTemplate.from_template(
        "{input}\n---\n주어진 기사를 읽고, 다음의 포맷에 맞춰 응답해라.  : {format_instruction}",
        partial_variables={"format_instruction": format_instruction})
    # HumanMessagePromptTemplate를 사용하여 프롬프트 템플릿 생성
    # format_instruction 변수를 사용하여, 요약이 어떻게 작성되어야 하는지를 명시
    prompt_template = ChatPromptTemplate.from_messages(
        [
            human_msg_prompt_template
        ],
    )
    chain = prompt_template | model | parser
    # chain은 프롬프트 템플릿, 모델, 그리고 파서를 연결하여 데이터 처리의 흐름을 만듭니다.
    result = chain.invoke({"input": description,"format_instruction":format_instruction}) # Summary클래스에서 정의한 모델에 맞춘 dict 타입
    update_query = f"""
        UPDATE news_content
        SET summary = %s
        WHERE news_info_id = %s;
        """
    values = (result["summary"], news_info_id)
    try:
        # 쿼리 실행
        cur.execute(update_query, values)
        # 변경 사항 커밋
        conn.commit()
        print(f"Record updated successfully! {news_info_id}")
    except Exception as e:
        # 오류 발생 시 롤백
        conn.rollback()
        print(f"Error updating record: {e}")

# 커서와 연결을 닫기
if cursor:
    cursor.close()
if conn:
    conn.close()
