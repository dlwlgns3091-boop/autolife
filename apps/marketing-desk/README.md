# 마케팅 데스크

마케팅 데스크 반복 업무 관리 앱.

## 실행

```bash
cd apps/marketing-desk
pip install -r requirements.txt
uvicorn src.main:app --port 8003 --reload
```

접속: http://localhost:8003

## 기능

- **대시보드**: 지금 할 일을 우선순위로 모아 표시
- **STEP 0**: 일회성 셋업 체크리스트 (체크 유지)
- **매주 루틴**: 주간 반복 체크리스트 (새 주 시작 버튼으로 초기화)
- **매월 루틴**: 월초/월중/월말 그룹 체크리스트
- **즉시처리**: 우선순위·마감일 기반 할일 관리, 일괄 등록, AI용 복사

## 테스트

```bash
cd apps/marketing-desk
pytest tests/ -v
```
