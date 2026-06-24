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


# ── STEP 0 ────────────────────────────────────────────────────────────────
def test_step0_create():
    r = client.post("/step0", json={"title": "초기 설정 A"})
    assert r.status_code == 201
    d = r.json()
    assert d["title"] == "초기 설정 A"
    assert d["checked"] is False


def test_step0_list():
    client.post("/step0", json={"title": "항목1"})
    client.post("/step0", json={"title": "항목2"})
    r = client.get("/step0")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_step0_toggle_check():
    item = client.post("/step0", json={"title": "체크 항목"}).json()
    r = client.patch(f"/step0/{item['id']}/check")
    assert r.json()["checked"] is True
    r2 = client.patch(f"/step0/{item['id']}/check")
    assert r2.json()["checked"] is False


def test_step0_update():
    item = client.post("/step0", json={"title": "원래 제목"}).json()
    r = client.put(f"/step0/{item['id']}", json={"title": "수정된 제목", "memo": "메모 추가"})
    assert r.json()["title"] == "수정된 제목"
    assert r.json()["memo"] == "메모 추가"


def test_step0_delete():
    item = client.post("/step0", json={"title": "삭제할 항목"}).json()
    r = client.delete(f"/step0/{item['id']}")
    assert r.status_code == 204
    assert len(client.get("/step0").json()) == 0


def test_step0_not_found():
    r = client.put("/step0/999", json={"title": "없음"})
    assert r.status_code == 404


# ── WEEKLY ────────────────────────────────────────────────────────────────
def test_weekly_create():
    r = client.post("/weekly", json={"title": "주간 업무"})
    assert r.status_code == 201
    assert r.json()["checked"] is False


def test_weekly_toggle():
    item = client.post("/weekly", json={"title": "주간"}).json()
    r = client.patch(f"/weekly/{item['id']}/check")
    assert r.json()["checked"] is True


def test_weekly_reset():
    item1 = client.post("/weekly", json={"title": "업무1"}).json()
    item2 = client.post("/weekly", json={"title": "업무2"}).json()
    client.patch(f"/weekly/{item1['id']}/check")
    client.patch(f"/weekly/{item2['id']}/check")
    r = client.post("/weekly/reset")
    assert r.status_code == 204
    items = client.get("/weekly").json()
    assert all(i["checked"] is False for i in items)
    assert len(items) == 2  # items preserved


def test_weekly_delete():
    item = client.post("/weekly", json={"title": "삭제"}).json()
    client.delete(f"/weekly/{item['id']}")
    assert len(client.get("/weekly").json()) == 0


# ── MONTHLY ───────────────────────────────────────────────────────────────
def test_monthly_create_valid_periods():
    for period in ["월초", "월중", "월말"]:
        r = client.post("/monthly", json={"title": f"{period} 업무", "period": period})
        assert r.status_code == 201
        assert r.json()["period"] == period


def test_monthly_invalid_period():
    r = client.post("/monthly", json={"title": "잘못된 구분", "period": "월요일"})
    assert r.status_code == 422


def test_monthly_grouped_order():
    client.post("/monthly", json={"title": "월말 업무", "period": "월말"})
    client.post("/monthly", json={"title": "월초 업무", "period": "월초"})
    client.post("/monthly", json={"title": "월중 업무", "period": "월중"})
    items = client.get("/monthly").json()
    periods = [i["period"] for i in items]
    first_idx = periods.index("월초")
    mid_idx = periods.index("월중")
    end_idx = periods.index("월말")
    assert first_idx < mid_idx < end_idx


def test_monthly_reset():
    r1 = client.post("/monthly", json={"title": "월초", "period": "월초"}).json()
    r2 = client.post("/monthly", json={"title": "월말", "period": "월말"}).json()
    client.patch(f"/monthly/{r1['id']}/check")
    client.patch(f"/monthly/{r2['id']}/check")
    client.post("/monthly/reset")
    items = client.get("/monthly").json()
    assert all(i["checked"] is False for i in items)
    assert len(items) == 2


def test_monthly_delete():
    item = client.post("/monthly", json={"title": "삭제", "period": "월중"}).json()
    client.delete(f"/monthly/{item['id']}")
    assert len(client.get("/monthly").json()) == 0


# ── IMMEDIATE ─────────────────────────────────────────────────────────────
def test_immediate_create_minimal():
    r = client.post("/immediate", json={"title": "빠른 처리"})
    assert r.status_code == 201
    d = r.json()
    assert d["title"] == "빠른 처리"
    assert d["priority"] == 3
    assert d["status"] == "pending"


def test_immediate_create_full():
    r = client.post("/immediate", json={
        "title": "마감 업무",
        "deadline": "2026-06-30",
        "priority": 5,
        "status": "in_progress",
        "memo": "중요"
    })
    assert r.status_code == 201
    d = r.json()
    assert d["deadline"] == "2026-06-30"
    assert d["priority"] == 5
    assert d["status"] == "in_progress"


def test_immediate_invalid_priority():
    r = client.post("/immediate", json={"title": "우선순위 오류", "priority": 6})
    assert r.status_code == 422


def test_immediate_invalid_status():
    r = client.post("/immediate", json={"title": "상태 오류", "status": "unknown"})
    assert r.status_code == 422


def test_immediate_list_sorted():
    client.post("/immediate", json={"title": "낮은 우선순위", "priority": 1})
    client.post("/immediate", json={"title": "높은 우선순위", "priority": 5})
    items = client.get("/immediate").json()
    undone = [i for i in items if i["status"] != "done"]
    assert undone[0]["priority"] >= undone[-1]["priority"]


def test_immediate_done_sorted_last():
    t1 = client.post("/immediate", json={"title": "완료", "priority": 5}).json()
    client.post("/immediate", json={"title": "미완료", "priority": 1})
    client.put(f"/immediate/{t1['id']}", json={"status": "done"})
    items = client.get("/immediate").json()
    assert items[-1]["status"] == "done"


def test_immediate_update():
    task = client.post("/immediate", json={"title": "수정 전"}).json()
    r = client.put(f"/immediate/{task['id']}", json={"title": "수정 후", "priority": 4})
    assert r.json()["title"] == "수정 후"
    assert r.json()["priority"] == 4


def test_immediate_delete():
    task = client.post("/immediate", json={"title": "삭제"}).json()
    client.delete(f"/immediate/{task['id']}")
    assert len(client.get("/immediate").json()) == 0


def test_immediate_not_found():
    r = client.put("/immediate/999", json={"title": "없음"})
    assert r.status_code == 404
