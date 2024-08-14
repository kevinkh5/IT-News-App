from flask import Flask, request, make_response, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from dotenv import load_dotenv
import os
from pathlib import Path
dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path)
app = Flask(__name__)
CORS(app) # (Cross-Origin Resource Sharing) 허용시키기

# PostgreSQL 데이터베이스 URI 설정
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv('user')}:{os.getenv('password')}@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('dbname')}'
# 성능향상을 위해(CPU 사용량 줄이기)
# SQLAlchemy가 모든 변경 사항을 추적하고 신호를 발행하여 변경을 기록하는 것을 비활성화
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# news_info 모델 정의
class news_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), nullable=False, index=True)
    title = db.Column(db.String(300), unique=True, nullable=False, index=True)
    author = db.Column(db.String(30), nullable=False)
    img_link = db.Column(db.String(255), nullable=True)
    destination_link = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<news_info {self.id}>'

# news_info 모델 정의
class news_content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_info_id = db.Column(db.Integer, db.ForeignKey('news_info.id'), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<news_content {self.news_info_id}>'

# 데이터베이스내 테이블 준비
with app.app_context():
    db.create_all()

# 첫 페이지 카드표시 라우터
@app.route("/newscards", methods=['GET'])
def newscards():
    try:
        data_info = news_info.query.order_by(news_info.created_at.desc()).limit(60).all() # 최근것 부터 최대 60개까지 가져오기
        allData = [{'id':data.id,'category': data.category, 'title': data.title,
                    'author':data.author,'img_link':data.img_link,
                    'destination_link':data.destination_link, 'date':data.date,
                    'created_at':data.created_at} for data in data_info]
        
        newscards_list = defaultdict(list)
        for newscards_data in allData:
            newscards_list[newscards_data["category"]].append(newscards_data)
    except Exception as e:
        print(e)
        response = {
            'status': 400,
            'message': 'Bad Request'
        }
        return make_response(jsonify(response), 400)
    # news_data를 json형식으로 변환 후 HTTP 200 응답생성
    return make_response(jsonify(newscards_list), 200)

# 카드 클릭후 디테일 페이지 표시 라우터
@app.route('/content',  methods=['GET'])
def content():
    # 쿼리 파라미터 가져오기
    category = request.args.get('category', default='', type=str)
    news_info_id = request.args.get('id', default='', type=str)
    print("category : ",category)
    print("news_info_id : ",news_info_id)
    try:
        target1 = news_info.query.filter_by(category=category, id=news_info_id).one()
    except Exception as e:
        print('target1')
        print(e)
        response = {
            'status': 400,
            'message': 'Bad Request: No content'
        }
        return make_response(jsonify(response), 400)
    
    try:
        target2 = news_content.query.filter_by(news_info_id=news_info_id).one()
    except Exception as e:
        print('target2')
        print(e)
        response = {
            'status': 400,
            'message': 'Bad Request: No content'
        }
        return make_response(jsonify(response), 400)

    content = {"category":category, 'news_info_id':news_info_id,
               'author':target1.author, 'date':target1.date,
               'img_link':target1.img_link, 'description':target2.description,
               'summary':target2.summary,'destination_link':target1.destination_link};

    return make_response(jsonify(content), 200)


@app.route('/audio/<filename>')
def get_audio(filename):
    return send_from_directory(Path(__file__).resolve().parent / 'audio', filename)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8082)