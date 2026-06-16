# 전세집 트래커

두 사람이 전세집 후보를 기록하고, 각자의 선호/가중치로 종합 점수를 매겨 비교하는 모바일 반응형 웹앱.

## 스택

- **백엔드**: Python 3.11+ / FastAPI / SQLite (SQLAlchemy)
- **프론트엔드**: 바닐라 HTML/CSS/JS (모바일 반응형, 폰 Safari 최적화)

## 로컬 실행 방법

### 1. 의존성 설치

```bash
cd apps/jeonse-tracker
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
uvicorn main:app --reload --port 8000
```

브라우저에서 `http://localhost:8000` 접속

폰에서 접속하려면 같은 Wi-Fi 환경에서:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
그리고 폰 브라우저에서 `http://<PC-IP>:8000` 접속

### 3. 초기 데이터

앱 최초 실행 시 자동으로 아래 데이터가 생성됩니다:
- 사용자: **소희**, **지훈**
- 선호 항목 및 기본 가중치:
  - 고정비용(월 지출) — 공통, 가중치 5
  - 방 넓이 — 소희, 가중치 4
  - 직주근접 — 지훈, 가중치 4
  - 집 컨디션(구조/연식) — 공통, 가중치 3
  - 평수 — 공통, 가중치 3

## 테스트 실행

```bash
cd apps/jeonse-tracker
pip install -r requirements.txt
pytest tests/ -v
```

## 기능 요약

| 화면 | 기능 |
|------|------|
| 후보 목록 | 합산 점수순 정렬, 지역/보증금/점수 요약 |
| 집 추가/수정 | 지역, 보증금, 면적, 방/화장실 수, 월 고정비, 링크, 메모, 상태 입력 |
| 상세 비교 | 두 사람 항목별 점수 나란히 비교, 총점 표시 |
| 가중치 설정 | 사용자별 항목 가중치를 슬라이더로 조정 |

## DB 파일

`jeonse.db` (SQLite) — 서버 실행 디렉터리에 자동 생성됨. 백업 시 이 파일 복사.
