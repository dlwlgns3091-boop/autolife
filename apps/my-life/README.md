# My Life

개인용 할일 관리 + 가계부 앱. 모바일 반응형 웹앱으로, 폰에서 접속 가능합니다.

## 기능

- **비밀번호 잠금**: 환경변수 `APP_PASSWORD`로 설정, 세션 쿠키로 유지
- **할일 탭**: 제목/우선순위/상태/마감일/메모, 필터(오늘·이번주·완료), 마감 지난 항목 빨간 강조
- **가계부 탭**: 수입·지출 내역 관리, 월별 요약, 분류별 합계
- **검색엔진 차단**: `noindex, nofollow` 메타태그 포함
- **Swagger**: `/docs` (로그인 후 접근 가능)

## 로컬 실행

```bash
cd apps/my-life

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정 (.env.example 참고)
cp .env.example .env
# .env 파일에서 APP_PASSWORD 설정

# 서버 실행
APP_PASSWORD=your_password uvicorn src.main:app --reload --port 8000
```

브라우저에서 http://localhost:8000 접속

## 테스트 실행

```bash
cd apps/my-life
pip install -r requirements.txt
pytest tests/ -v
```

## 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `APP_PASSWORD` | (필수) | 앱 접속 비밀번호 |
| `PORT` | `8000` | 서버 포트 |
| `DATABASE_URL` | `sqlite:///./my_life.db` | SQLite DB 경로 |

## Railway 배포

1. [Railway](https://railway.app)에서 새 프로젝트 생성 → GitHub 레포 연결

2. **루트 디렉터리** 설정: `apps/my-life`

3. **Start Command** 설정:
   ```
   uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

4. **환경변수** 설정 (Railway Variables):
   ```
   APP_PASSWORD=your_secure_password
   DATABASE_URL=sqlite:////data/my_life.db
   ```

5. **볼륨 마운트** (데이터 영구 보존): Railway의 Volume 기능으로 `/data` 경로 마운트

6. 배포 후 Railway가 제공하는 URL로 접속
