from datetime import date
from sqlalchemy.orm import Session
from .models import Step0Item, WeeklyRoutine, MonthlyRoutine, ImmediateTask


def run_seed(db: Session):
    if db.query(Step0Item).count() > 0:
        return

    step0_titles = [
        "홈피 커넥터 일괄 업데이트 (구버전→v2.15)",
        "제니스라인 커넥터 빈 응답 별도 점검",
        "플레이스 순위체크 ON (병원별 메인키워드 저장)",
        "GEO 엔티티 배포 (미배포 병원 JSON-LD)",
        "GEO 페르소나 활성화",
        "웹문서 점검 (참여 ON·게시판 확인)",
    ]
    for i, title in enumerate(step0_titles):
        db.add(Step0Item(title=title, order=i))

    weekly_titles = [
        "웹문서 자동발행 결과 확인, 실패 건 재시도",
        "플레이스 신규 리뷰 답글(부정 우선), 순위 급변 확인",
        "리뷰 갭 경보 뜬 병원 확인",
        "홈페이지 연결상태 오류 점검",
    ]
    for i, title in enumerate(weekly_titles):
        db.add(WeeklyRoutine(title=title, order=i))

    for i, title in enumerate([
        "GEO 정찰 스캔 실행 (이번 달 4~6곳)",
        "플레이스 전체 분석 실행",
        "이번 달 병원별 완료 기준 확정",
    ]):
        db.add(MonthlyRoutine(title=title, group="early", order=i))

    for i, title in enumerate([
        "GEO 미노출 질문 콘텐츠 발행 / 홈피 진단 개발자 전달",
        "리뷰 갭 보강",
        "플레이스 수정필요 섹션 처리",
    ]):
        db.add(MonthlyRoutine(title=title, group="mid", order=i))

    for i, title in enumerate([
        "GEO 증명 리포트 (T0 대비 변화)",
        "플레이스 순위 변화 정리",
        "못 끝낸 건 이월 목록 기록",
    ]):
        db.add(MonthlyRoutine(title=title, group="late", order=i))

    for item in [
        {"title": "제니스라인 커넥터 빈 응답 점검", "priority": 5},
        {"title": "리뷰 갭 경보 2곳 (아프로 9%, 바른내일 45%)", "priority": 4},
        {"title": "구버전 커넥터 일괄 업데이트 (365서울차오름 외)", "priority": 4},
        {"title": "GEO 엔티티 미배포 (서울그랜드, 바른이디자인, 바른이바른얼굴, 시그니처)", "priority": 3},
        {"title": "GEO 정찰 대상 4~6곳 선정", "priority": 3},
    ]:
        db.add(ImmediateTask(title=item["title"], priority=item["priority"], status="pending"))

    db.commit()
