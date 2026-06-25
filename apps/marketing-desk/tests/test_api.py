import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from src.main import app

TEST_DB_URL = "sqlite:///./test_marketing_desk.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


# ── Daily ────────────────────────────────────────────────────────────────

def test_daily_create():
    r = client.post("/daily", json={"title": "온라인 모니터링"})
    assert r.status_code == 201
    d = r.json()
    assert d["title"] == "온라인 모니터링"
    assert d["is_checked"] is False


def test_daily_list():
    client.post("/daily", json={"title": "항목A"})
    client.post("/daily", json={"title": "항목B"})
    r = client.get("/daily")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_daily_check():
    item = client.post("/daily", json={"title": "체크"}).json()
    r = client.patch("/daily/{}/check?checked=true".format(item["id"]))
    assert r.json()["is_checked"] is True


def test_daily_uncheck():
    item = client.post("/daily", json={"title": "체크 해제"}).json()
    client.patch("/daily/{}/check?checked=true".format(item["id"]))
    r = client.patch("/daily/{}/check?checked=false".format(item["id"]))
    assert r.json()["is_checked"] is False


def test_daily_update():
    item = client.post("/daily", json={"title": "원래"}).json()
    r = client.put("/daily/{}".format(item["id"]), json={"title": "수정됨"})
    assert r.json()["title"] == "수정됨"


def test_daily_delete():
    item = client.post("/daily", json={"title": "삭제"}).json()
    r = client.delete("/daily/{}".format(item["id"]))
    assert r.status_code == 204
    assert len(client.get("/daily").json()) == 0


def test_daily_reset():
    item = client.post("/daily", json={"title": "루틴"}).json()
    client.patch("/daily/{}/check?checked=true".format(item["id"]))
    assert client.get("/daily").json()[0]["is_checked"] is True
    r = client.post("/daily/reset")
    assert r.status_code == 204
    assert client.get("/daily").json()[0]["is_checked"] is False


# ── Month Start ──────────────────────────────────────────────────────────

def test_month_start_task_create():
    r = client.post("/month-start/tasks", json={"title": "원고 작성"})
    assert r.status_code == 201
    assert r.json()["is_checked"] is False


def test_month_start_task_check():
    item = client.post("/month-start/tasks", json={"title": "원고"}).json()
    r = client.patch("/month-start/tasks/{}/check?checked=true".format(item["id"]))
    assert r.json()["is_checked"] is True


def test_month_start_task_delete():
    item = client.post("/month-start/tasks", json={"title": "삭제"}).json()
    r = client.delete("/month-start/tasks/{}".format(item["id"]))
    assert r.status_code == 204


def test_month_start_cafe_list():
    r = client.get("/month-start/hospitals/cafe")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_month_start_review_list():
    r = client.get("/month-start/hospitals/review")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_month_start_reset():
    item = client.post("/month-start/tasks", json={"title": "리셋"}).json()
    client.patch("/month-start/tasks/{}/check?checked=true".format(item["id"]))
    r = client.post("/month-start/reset")
    assert r.status_code == 204
    assert client.get("/month-start/tasks").json()[0]["is_checked"] is False


# ── Month End ────────────────────────────────────────────────────────────

def test_month_end_create():
    r = client.post("/month-end", json={"title": "팝업 등록"})
    assert r.status_code == 201


def test_month_end_check():
    item = client.post("/month-end", json={"title": "체크"}).json()
    r = client.patch("/month-end/{}/check?checked=true".format(item["id"]))
    assert r.json()["is_checked"] is True


def test_month_end_reset():
    item = client.post("/month-end", json={"title": "리셋"}).json()
    client.patch("/month-end/{}/check?checked=true".format(item["id"]))
    r = client.post("/month-end/reset")
    assert r.status_code == 204
    assert client.get("/month-end").json()[0]["is_checked"] is False


def test_month_end_delete():
    item = client.post("/month-end", json={"title": "삭제"}).json()
    r = client.delete("/month-end/{}".format(item["id"]))
    assert r.status_code == 204


# ── Weekly Tasks ─────────────────────────────────────────────────────────

def test_weekly_create():
    r = client.post("/weekly-tasks", json={"title": "발행 현황 점검"})
    assert r.status_code == 201
    assert r.json()["is_checked"] is False


def test_weekly_check():
    item = client.post("/weekly-tasks", json={"title": "점검"}).json()
    r = client.patch("/weekly-tasks/{}/check?checked=true".format(item["id"]))
    assert r.json()["is_checked"] is True


def test_weekly_reset():
    item = client.post("/weekly-tasks", json={"title": "루틴"}).json()
    client.patch("/weekly-tasks/{}/check?checked=true".format(item["id"]))
    r = client.post("/weekly-tasks/reset")
    assert r.status_code == 204
    assert client.get("/weekly-tasks").json()[0]["is_checked"] is False


def test_weekly_delete():
    item = client.post("/weekly-tasks", json={"title": "삭제"}).json()
    r = client.delete("/weekly-tasks/{}".format(item["id"]))
    assert r.status_code == 204


# ── Always On ────────────────────────────────────────────────────────────

def test_always_create():
    r = client.post("/always", json={"title": "팝업 처리", "priority": 5})
    assert r.status_code == 201
    d = r.json()
    assert d["title"] == "팝업 처리"
    assert d["priority"] == 5
    assert d["status"] == "pending"


def test_always_list_excludes_done():
    t = client.post("/always", json={"title": "완료 항목"}).json()
    client.patch("/always/{}/status?status=done".format(t["id"]))
    r = client.get("/always")
    assert all(x["status"] != "done" for x in r.json())


def test_always_list_done():
    t = client.post("/always", json={"title": "완료"}).json()
    client.patch("/always/{}/status?status=done".format(t["id"]))
    r = client.get("/always?status=done")
    assert len(r.json()) == 1


def test_always_update():
    t = client.post("/always", json={"title": "전"}).json()
    r = client.put("/always/{}".format(t["id"]), json={"title": "후", "priority": 4})
    assert r.json()["title"] == "후"
    assert r.json()["priority"] == 4


def test_always_delete():
    t = client.post("/always", json={"title": "삭제"}).json()
    r = client.delete("/always/{}".format(t["id"]))
    assert r.status_code == 204


def test_always_invalid_status():
    t = client.post("/always", json={"title": "항목"}).json()
    r = client.patch("/always/{}/status?status=invalid".format(t["id"]))
    assert r.status_code == 400


def test_always_bulk_preview():
    r = client.post("/always/bulk/preview", json={"text": "업무A | 5 | 2026-07-01 | 메모\n업무B | 3"})
    assert r.status_code == 200
    d = r.json()
    assert d["count"] == 2
    assert d["preview"][0]["title"] == "업무A"
    assert d["preview"][0]["priority"] == 5
    assert d["preview"][1]["priority"] == 3


def test_always_bulk_create():
    r = client.post("/always/bulk", json={"text": "작업A | 4 | 2026-07-10\n작업B | 2"})
    assert r.status_code == 201
    items = r.json()
    assert len(items) == 2
    assert items[0]["title"] == "작업A"
    assert items[0]["priority"] == 4


# ── Calendar ─────────────────────────────────────────────────────────────

def test_calendar_create():
    r = client.post("/calendar", json={"event_date": "2026-07-01", "title": "회의", "memo": "메모"})
    assert r.status_code == 201
    d = r.json()
    assert d["event_date"] == "2026-07-01"
    assert d["title"] == "회의"


def test_calendar_list_by_month():
    client.post("/calendar", json={"event_date": "2026-07-01", "title": "7월 일정"})
    client.post("/calendar", json={"event_date": "2026-08-01", "title": "8월 일정"})
    r = client.get("/calendar?year=2026&month=7")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["title"] == "7월 일정"


def test_calendar_update():
    ev = client.post("/calendar", json={"event_date": "2026-07-05", "title": "원래"}).json()
    r = client.put("/calendar/{}".format(ev["id"]), json={"title": "수정됨"})
    assert r.json()["title"] == "수정됨"


def test_calendar_delete():
    ev = client.post("/calendar", json={"event_date": "2026-07-05", "title": "삭제"}).json()
    r = client.delete("/calendar/{}".format(ev["id"]))
    assert r.status_code == 204


# ── Dashboard ────────────────────────────────────────────────────────────

def test_dashboard_empty():
    r = client.get("/dashboard")
    assert r.status_code == 200
    d = r.json()
    assert "items" in d
    assert "daily" in d
    assert "month_start" in d
    assert "month_end" in d
    assert "weekly" in d
    assert "always" in d
    assert "current_period" in d
    assert "today" in d


def test_dashboard_shows_unchecked_daily():
    client.post("/daily", json={"title": "매일 업무"})
    r = client.get("/dashboard?limit=0")
    d = r.json()
    daily_items = [i for i in d["items"] if i["type"] == "daily"]
    assert len(daily_items) == 1


def test_dashboard_hides_checked():
    item = client.post("/daily", json={"title": "완료 항목"}).json()
    client.patch("/daily/{}/check?checked=true".format(item["id"]))
    r = client.get("/dashboard?limit=0")
    daily_items = [i for i in r.json()["items"] if i["type"] == "daily"]
    assert len(daily_items) == 0


def test_dashboard_limit():
    for i in range(5):
        client.post("/daily", json={"title": "항목{}".format(i)})
    r = client.get("/dashboard?limit=3")
    assert len(r.json()["items"]) <= 3


def test_dashboard_progress_counts():
    client.post("/daily", json={"title": "항목1"})
    client.post("/daily", json={"title": "항목2"})
    item = client.post("/daily", json={"title": "항목3"}).json()
    client.patch("/daily/{}/check?checked=true".format(item["id"]))
    r = client.get("/dashboard?limit=0")
    d = r.json()
    assert d["daily"]["total"] == 3
    assert d["daily"]["checked"] == 1
