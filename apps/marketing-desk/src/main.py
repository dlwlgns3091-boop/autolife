from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base, get_db, run_migrations
from .models import Step0Item, WeeklyItem, MonthlyItem, ImmediateTask
from .routers import step0, weekly, monthly, immediate


def _seed(db):
    step0_seeds = [
        "홈피 커넥터 일괄 업데이트 (구버전→v2.15)",
        "제니스라인 커넥터 빈 응답 별도 점검",
        "플레이스 순위체크 ON (병원별 메인키워드 저장)",
        "GEO 엔티티 배포 (미배포 병원 JSON-LD)",
        "GEO 페르소나 활성화",
        "웹문서 점검 (참여 ON·게시판 확인)",
    ]
    for i, title in enumerate(step0_seeds):
        db.add(Step0Item(title=title, sort_order=i))

    weekly_seeds = [
        "웹문서 자동발행 결과 확인, 실패 건 재시도",
        "플레이스 신규 리뷰 답글 (부정 우선), 순위 급변 확인",
        "리뷰 갭 경보 뜬 병원 확인",
        "홈페이지 연결상태 오류 점검",
    ]
    for i, title in enumerate(weekly_seeds):
        db.add(WeeklyItem(title=title, sort_order=i))

    monthly_seeds = [
        ("월초", "GEO 정찰 스캔 실행 (이번 달 4~6곳)"),
        ("월초", "플레이스 전체 분석 실행"),
        ("월초", "이번 달 병원별 완료 기준 확정"),
        ("월중", "GEO 미노출 질문 콘텐츠 발행 / 홈피 진단 개발자 전달"),
        ("월중", "리뷰 갭 보강"),
        ("월중", "플레이스 수정필요 섹션 처리"),
        ("월말", "GEO 증명 리포트 (T0 대비 변화)"),
        ("월말", "플레이스 순위 변화 정리"),
        ("월말", "못 끝낸 건 이월 목록 기록"),
    ]
    period_counters: dict = {}
    for period, title in monthly_seeds:
        order = period_counters.get(period, 0)
        db.add(MonthlyItem(title=title, period=period, sort_order=order))
        period_counters[period] = order + 1

    immediate_seeds = [
        ("제니스라인 커넥터 빈 응답 점검", 5),
        ("리뷰 갭 경보 2곳 (아프로 9%, 바른내일 45%)", 4),
        ("구버전 커넥터 일괄 업데이트 (365서울차오름 외)", 4),
        ("GEO 엔티티 미배포 (서울그랜드, 바른이디자인, 바른이바른얼굴, 시그니처)", 3),
        ("GEO 정찰 대상 4~6곳 선정", 3),
    ]
    for title, priority in immediate_seeds:
        db.add(ImmediateTask(title=title, priority=priority))

    db.commit()


@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_migrations()
    db = next(get_db())
    try:
        if db.query(Step0Item).count() == 0 and db.query(WeeklyItem).count() == 0:
            _seed(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Marketing Desk", description="마케팅 데스크 업무 관리 앱", version="1.0.0", lifespan=lifespan)

app.include_router(step0.router)
app.include_router(weekly.router)
app.include_router(monthly.router)
app.include_router(immediate.router)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))
