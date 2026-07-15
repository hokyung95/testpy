# pyrefly: ignore [missing-import]
import pugsql
import duckdb

# 1. SQL 파일이 있는 경로 로드
queries = pugsql.module('./resource/sql')

# 2. DuckDB 인메모리 커넥션 연결
# duckdb-engine을 설치했으므로 SQLAlchemy 커넥션 스트링을 사용합니다.
print("Duckdb 연결 전.")
queries.connect('duckdb:///:memory:')
print("연결 성공")
# 3. 트랜잭션 내에서 DDL, DML 및 조회 수행
with queries.transaction():
    # 테이블 생성 (DDL 실행)
    queries.create_users_table()
    print("테이블이 확인되었거나 생성되었습니다.")

    # 데이터 삽입 (DML 실행)
    queries.insert_user(id=1, name='김철수', email='chulsoo@example.com')
    queries.insert_user(id=2, name='이영희', email='younghee@example.com')
    print("데이터가 입력되었습니다.")

    # 확인 조회
    print("전체 사용자 목록 조회:")
    users = queries.get_all_users()
    for u in users:
        print(u)