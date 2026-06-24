# Marketing Desk

마케팅 데스크 반복 업무 관리 앱.

## 화면 구성

| 탭 | 설명 |
|---|---|
| STEP 0 | 일회성 셋업 체크리스트 |
| 매주 루틴 | 매주 반복 업무 체크리스트 (새 주 시작 버튼으로 초기화) |
| 매월 루틴 | 월초/월중/월말 그룹별 체크리스트 (새 달 시작 버튼으로 초기화) |
| 즉시처리 | 마감일·우선순위 있는 즉시 처리 할일 목록 |

## 실행

```bash
cd apps/marketing-desk
pip install -r requirements.txt
uvicorn src.main:app --port 8003 --reload
```

브라우저에서 http://localhost:8003 접속.

## 테스트

```bash
cd apps/marketing-desk
pytest tests/ -v
```

## 기술 스택

- FastAPI + SQLite (SQLAlchemy)
- 모바일 대응 단일 HTML 페이지
- 포트: 8003
