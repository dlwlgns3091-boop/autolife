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


# --- STEP 0 ---
def test_step0_create():
    r = client.post("/step0", json={"title": "초기 설정 항목"})
    assert r.status_code == 201
    d = r.json()
    assert d["title"] == "초기 설정 항목"
    assert d["is_checked"] is False


def test_step0_list():
    client.post("/step0", json={"title": "항목A"})
    client.post("/step0", json={"title": "항목B"})
    r = client.get("/step0")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_step0_check():
    item = client.post("/step0", json={"title": "체크 테스트"}).json()
    r = client.patch(f"/step0/{item['id']}/check?checked=true")
    assert r.json()["is_checked"] is True


def test_step0_uncheck():
    item = client.post("/step0", json={"title": "체크 해제"}).json()
    client.patch(f"/step0/{item['id']}/check?checked=true")
    r = client.patch(f"/step0/{item['id']}/check?checked=false")
    assert r.json()["is_checked"] is False


def test_step0_update():
    item = client.post("/step0", json={"title": "원래 제목", "memo": "원래 메모"}).json()
    r = client.put(f"/step0/{item['id']}", json={"title": "새 제목", "memo": "새 메모"})
    assert r.json()["title"] == "새 제목"
    assert r.json()["memo"] == "새 메모"


def test_step0_delete():
    item = client.post("/step0", json={"title": "삭제"}).json()
    r = client.delete(f"/step0/{item['id']}")
    assert r.status_code == 204
    assert len(client.get("/step0").json()) == 0


# --- WEEKLY ---
def test_weekly_create():
    r = client.post("/weekly", json={"title": "주간 루틴 항목"})
    assert r.status_code == 201
    assert r.json()["is_checked"] is False


def test_weekly_reset():
    item = client.post("/weekly", json={"title": "루틴"}).json()
    client.patch(f"/weekly/{item['id']}/check?checked=true")
    assert client.get("/weekly").json()[0]["is_checked"] is True
    r = client.post("/weekly/reset")
    assert r.status_code == 204
    assert client.get("/weekly").json()[0]["is_checked"] is False


def test_weekly_delete():
    item = client.post("/weekly", json={"title": "삭제"}).json()
    client.delete(f"/weekly/{item['id']}")
    assert len(client.get("/weekly").json()) == 0


# --- MONTHLY ---
def test_monthly_create_early():
    r = client.post("/monthly", json={"title": "월초 업무", "group": "early"})
    assert r.status_code == 201
    assert r.json()["group"] == "early"


def test_monthly_create_all_groups():
    client.post("/monthly", json={"title": "월초", "group": "early"})
    client.post("/monthly", json={"title": "월중", "group": "mid"})
    client.post("/monthly", json={"title": "월말", "group": "late"})
    r = client.get("/monthly")
    assert len(r.json()) == 3
    groups = [i["group"] for i in r.json()]
    assert "early" in groups and "mid" in groups and "late" in groups


def test_monthly_invalid_group():
    r = client.post("/monthly", json={"title": "잘못된 그룹", "group": "invalid"})
    assert r.status_code == 400


def test_monthly_reset():
    item = client.post("/monthly", json={"title": "리셋 테스트", "group": "mid"}).json()
    client.patch(f"/monthly/{item['id']}/check?checked=true")
    client.post("/monthly/reset")
    assert client.get("/monthly").json()[0]["is_checked"] is False


# --- IMMEDIATE ---
def test_immediate_create():
    r = client.post("/immediate", json={"title": "즉시 처리 항목", "priority": 5})
    assert r.status_code == 201
    d = r.json()
    assert d["title"] == "즉시 처리 항목"
    assert d["priority"] == 5
    assert d["status"] == "pending"


def test_immediate_list_excludes_done():
    t = client.post("/immediate", json={"title": "완료 항목"}).json()
    client.patch(f"/immediate/{t['id']}/status?status=done")
    r = client.get("/immediate")
    assert all(x["status"] != "done" for x in r.json())


def test_immediate_list_done():
    t = client.post("/immediate", json={"title": "완료"}).json()
    client.patch(f"/immediate/{t['id']}/status?status=done")
    r = client.get("/immediate?status=done")
    assert len(r.json()) == 1


def test_immediate_update():
    t = client.post("/immediate", json={"title": "업데이트 전"}).json()
    r = client.put(f"/immediate/{t['id']}", json={"title": "업데이트 후", "priority": 4})
    assert r.json()["title"] == "업데이트 후"
    assert r.json()["priority"] == 4


def test_immediate_delete():
    t = client.post("/immediate", json={"title": "삭제"}).json()
    r = client.delete(f"/immediate/{t['id']}")
    assert r.status_code == 204


def test_immediate_sorted_by_priority():
    client.post("/immediate", json={"title": "낮음", "priority": 1})
    client.post("/immediate", json={"title": "높음", "priority": 5})
    r = client.get("/immediate")
    items = r.json()
    assert items[0]["priority"] >= items[-1]["priority"]


# --- BULK ---
def test_bulk_preview():
    r = client.post("/immediate/bulk/preview", json={"text": "리뷰 처리 | 5 | 2026-07-01 | 메모\nGEO 배포 | 3"})
    assert r.status_code == 200
    d = r.json()
    assert d["count"] == 2
    assert d["preview"][0]["title"] == "리뷰 처리"
    assert d["preview"][0]["priority"] == 5
    assert d["preview"][1]["priority"] == 3


def test_bulk_create():
    r = client.post("/immediate/bulk", json={"text": "업무A | 4 | 2026-07-10\n업무B | 2"})
    assert r.status_code == 201
    items = r.json()
    assert len(items) == 2
    assert items[0]["title"] == "업무A"
    assert items[0]["priority"] == 4


# --- DASHBOARD ---
def test_dashboard_empty():
    r = client.get("/dashboard")
    assert r.status_code == 200
    d = r.json()
    assert "items" in d
    assert "step0" in d
    assert "weekly" in d
    assert "monthly" in d
    assert "immediate" in d
    assert "current_period" in d


def test_dashboard_shows_unchecked_step0():
    client.post("/step0", json={"title": "미완료 셋업"})
    r = client.get("/dashboard?limit=0")
    d = r.json()
    step0_items = [i for i in d["items"] if i["type"] == "step0"]
    assert len(step0_items) == 1


def test_dashboard_limit():
    for i in range(5):
        client.post("/step0", json={"title": f"항목{i}"})
    r = client.get("/dashboard?limit=3")
    assert len(r.json()["items"]) <= 3


def test_dashboard_summary_counts():
    client.post("/step0", json={"title": "셋업1"})
    client.post("/step0", json={"title": "셋업2"})
    item = client.post("/step0", json={"title": "셋업3"}).json()
    client.patch(f"/step0/{item['id']}/check?checked=true")
    r = client.get("/dashboard?limit=0")
    d = r.json()
    assert d["step0"]["total"] == 3
    assert d["step0"]["checked"] == 1


def test_dashboard_hides_checked_items():
    item = client.post("/step0", json={"title": "완료된 항목"}).json()
    client.patch(f"/step0/{item['id']}/check?checked=true")
    r = client.get("/dashboard?limit=0")
    step0_items = [i for i in r.json()["items"] if i["type"] == "step0"]
    assert len(step0_items) == 0
