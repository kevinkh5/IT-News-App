from app import app

if __name__ == "__main__":
    CORS(app) # (Cross-Origin Resource Sharing) 허용시키기

    # PostgreSQL 데이터베이스 URI 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv('user')}:{os.getenv('password')}@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('dbname')}'
    # 성능향상을 위해(CPU 사용량 줄이기)
    # SQLAlchemy가 모든 변경 사항을 추적하고 신호를 발행하여 변경을 기록하는 것을 비활성화
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.run(host='0.0.0.0', port=80)
