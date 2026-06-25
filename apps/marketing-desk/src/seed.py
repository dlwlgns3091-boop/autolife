from sqlalchemy.orm import Session
from .models import (
    DailyTask, MonthStartTask, MonthStartHospitalCafe, MonthStartHospitalReview,
    MonthEndTask, WeeklyTask,
)


def run_seed(db: Session):
    if db.query(DailyTask).count() > 0:
        return

    daily_titles = [
        "온라인 모니터링 (홈페이지 이상·오류 일괄 점검)",
        "애드몽 콘솔 대기 건 확인·처리",
        "홈페이지 요청 처리(팝업·공지·게시판·오류)",
        "카페 발행글 삭제 점검(발행 링크 직접 접속)",
        "삭제된 글 새 원고 작성해 재발행 요청",
    ]
    for i, title in enumerate(daily_titles):
        db.add(DailyTask(title=title, order=i))

    ms_titles = [
        "카페 침투 원고 작성 (6곳 × 약 10건)",
        "후기(구글리뷰) 원고 작성 (21곳 × 약 5개)",
        "외주에 일괄 실행 요청",
        "요청 목록 기록",
    ]
    for i, title in enumerate(ms_titles):
        db.add(MonthStartTask(title=title, order=i))

    cafe_hospitals = [
        "새오름피부과", "배곧샤인", "연세바로",
        "레메디한방병원", "서울성장하는", "송병재",
    ]
    for i, name in enumerate(cafe_hospitals):
        db.add(MonthStartHospitalCafe(name=name, order=i))

    review_hospitals = [
        "배곧샤인", "연세바로", "바른이바른얼굴", "타임", "연세그랑스마일",
        "제니스라인", "아프로", "서울바른(청주)", "서울바른(김포)", "서울류준하",
        "좋아서하는", "연세위드", "활짝웃는", "연세바른", "바른내일",
        "연세메이트", "레메디한방병원", "서울성장하는", "탁월한", "송병재", "바르다",
    ]
    for i, name in enumerate(review_hospitals):
        db.add(MonthStartHospitalReview(name=name, order=i))

    me_titles = [
        "병원별 진료일정 수령 확인(안 온 곳 리마인드)",
        "피그마로 팝업 이미지 제작",
        "콘솔에서 병원별 팝업/공지 등록(하나씩)",
        "게시 확인",
    ]
    for i, title in enumerate(me_titles):
        db.add(MonthEndTask(title=title, order=i))

    weekly_titles = [
        "카페·후기 발행 현황 점검(요청분 다 올라갔나)",
        "이번 달 진행상황 vs 할 일 대조",
        "콘솔 대기·미처리 정리",
    ]
    for i, title in enumerate(weekly_titles):
        db.add(WeeklyTask(title=title, order=i))

    db.commit()
