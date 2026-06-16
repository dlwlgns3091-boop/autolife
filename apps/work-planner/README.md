# work-planner

업무를 우선순위·마감순으로 계획하고, 반복 업무는 템플릿 버튼으로 빠르게 추가하는 모바일 반응형 웹앱.

## 스택

| 항목 | 내용 |
|------|------|
| 백엔드 | Python 3.11+ + FastAPI |
| DB | SQLite |
| 프론트 | 순수 HTML/CSS/JS (모바일 반응형) |

## 주요 기능

- **업무 종류 관리** — 사용자 정의 카테고리 추가/수정/삭제
- **업무 CRUD** — 제목, 종류, 치과, 우선순위(1~5), 마감일, 상태, 메모
- **반복 업무 템플릿** — 버튼 한 번으로 오늘 날짜 업무 즉시 생성
- **계획 보기** — 우선순위 높은 순 → 마감 임박 순 정렬, 기한 초과 강조
- **필터** — 오늘 / 이번 주 / 업무 종류별 / 치과명
- **빠른 처리** — 인라인 완료 체크, 우선순위 드롭다운 즉시 변경

## 로컬 실행

### 1. 의존성 설치

```bash
cd apps/work-planner
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
uvicorn src.main:app --reload --port 8000
```

### 3. 브라우저에서 확인

- 앱: http://localhost:8000
- Swagger API 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 테스트 실행

```bash
cd apps/work-planner
pytest tests/ -v
```

## API 개요

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /api/categories | 업무 종류 목록 |
| POST | /api/categories | 업무 종류 생성 |
| PUT | /api/categories/{id} | 업무 종류 수정 |
| DELETE | /api/categories/{id} | 업무 종류 삭제 |
| GET | /api/tasks | 업무 목록 (필터/정렬) |
| GET | /api/tasks/summary | 오늘/초과/진행중 요약 |
| POST | /api/tasks | 업무 생성 |
| GET | /api/tasks/{id} | 업무 상세 |
| PATCH | /api/tasks/{id} | 업무 수정 |
| DELETE | /api/tasks/{id} | 업무 삭제 |
| GET | /api/templates | 템플릿 목록 |
| POST | /api/templates | 템플릿 생성 |
| PUT | /api/templates/{id} | 템플릿 수정 |
| DELETE | /api/templates/{id} | 템플릿 삭제 |
| POST | /api/templates/{id}/apply | 템플릿으로 오늘 업무 생성 |

전체 Swagger 문서: http://localhost:8000/docs
