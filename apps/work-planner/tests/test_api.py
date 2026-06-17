import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from src.main import app

TEST_DB_URL = "sqlite:///./test_work_planner.db"
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


# --- Categories ---
def test_create_category():
    r = client.post("/categories", json={"name": "증례"})
    assert r.status_code == 201
    assert r.json()["name"] == "증례"


def test_list_categories():
    client.post("/categories", json={"name": "블로그"})
    r = client.get("/categories")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_update_category():
    r = client.post("/categories", json={"name": "구버전"})
    cid = r.json()["id"]
    r2 = client.put(f"/categories/{cid}", json={"name": "새버전"})
    assert r2.json()["name"] == "새버전"


def test_delete_category():
    r = client.post("/categories", json={"name": "임시"})
    cid = r.json()["id"]
    r2 = client.delete(f"/categories/{cid}")
    assert r2.status_code == 204
    assert len(client.get("/categories").json()) == 0


# --- Tasks ---
def test_create_task_title_only():
    r = client.post("/tasks", json={"title": "제목만"})
    assert r.status_code == 201
    d = r.json()
    assert d["title"] == "제목만"
    assert d["priority"] == 3
    assert d["status"] == "pending"


def test_create_task_defaults_to_direct():
    r = client.post("/tasks", json={"title": "직접 추가 업무"})
    assert r.status_code == 201
    d = r.json()
    assert d["task_source"] == "직접"


def test_create_task_full():
    cat = client.post("/categories", json={"name": "회의"}).json()
    r = client.post("/tasks", json={
        "title": "주간 회의",
        "category_id": cat["id"],
        "priority": 5,
        "status": "in_progress",
        "deadline": "2026-06-20",
        "recurrence": "weekly",
        "memo": "팀 전체 참석"
    })
    assert r.status_code == 201
    d = r.json()
    assert d["category_name"] == "회의"
    assert d["recurrence"] == "weekly"


def test_task_list_sorted_by_priority():
    client.post("/tasks", json={"title": "낮은 우선순위", "priority": 1})
    client.post("/tasks", json={"title": "높은 우선순위", "priority": 5})
    r = client.get("/tasks")
    items = r.json()
    assert items[0]["priority"] >= items[-1]["priority"]


def test_task_status_update():
    t = client.post("/tasks", json={"title": "상태 변경 테스트"}).json()
    r = client.patch(f"/tasks/{t['id']}/status?status=in_progress")
    assert r.json()["status"] == "in_progress"


def test_task_priority_update():
    t = client.post("/tasks", json={"title": "우선순위 변경"}).json()
    r = client.patch(f"/tasks/{t['id']}/priority?priority=5")
    assert r.json()["priority"] == 5


def test_task_filter_done():
    t = client.post("/tasks", json={"title": "완료 업무"}).json()
    client.patch(f"/tasks/{t['id']}/status?status=done")
    r = client.get("/tasks?filter=done")
    assert len(r.json()) == 1
    r2 = client.get("/tasks")
    assert all(x["status"] != "done" for x in r2.json())


def test_delete_task():
    t = client.post("/tasks", json={"title": "삭제할 업무"}).json()
    client.delete(f"/tasks/{t['id']}")
    r = client.get("/tasks")
    assert all(x["id"] != t["id"] for x in r.json())


def test_summary():
    r = client.get("/tasks/summary")
    assert r.status_code == 200
    d = r.json()
    assert "today_count" in d
    assert "overdue_count" in d
    assert "in_progress_count" in d


# --- Bulk ---
def test_bulk_preview():
    r = client.post("/tasks/bulk/preview", json={"text": "업무1 | 블로그 | 5 | 2026-06-18 | 메모\n업무2 | | 3"})
    assert r.status_code == 200
    d = r.json()
    assert d["count"] == 2
    assert d["preview"][0]["title"] == "업무1"
    assert d["preview"][0]["priority"] == 5
    assert d["preview"][1]["priority"] == 3


def test_bulk_create():
    r = client.post("/tasks/bulk", json={"text": "업무A | 증례 | 4\n업무B | | 2 | 2026-06-19"})
    assert r.status_code == 201
    items = r.json()
    assert len(items) == 2
    assert items[0]["title"] == "업무A"
    assert items[1]["deadline"] == "2026-06-19"


def test_bulk_create_sets_direct_source():
    r = client.post("/tasks/bulk", json={"text": "일괄A | 블로그 | 3\n일괄B"})
    assert r.status_code == 201
    items = r.json()
    assert all(item["task_source"] == "직접" for item in items)


# --- Templates ---
def test_create_template():
    r = client.post("/templates", json={"title": "일일 보고서", "default_priority": 4, "deadline_offset_days": 0})
    assert r.status_code == 201
    d = r.json()
    assert d["deadline_offset_days"] == 0


def test_create_task_from_template():
    t = client.post("/templates", json={"title": "주간 회의록", "default_priority": 3, "deadline_offset_days": 2}).json()
    r = client.post(f"/templates/{t['id']}/create-task")
    assert r.status_code == 201
    d = r.json()
    assert d["title"] == "주간 회의록"
    assert d["deadline"] is not None


def test_template_task_source_is_recurring():
    tpl = client.post("/templates", json={"title": "반복 업무 템플릿", "default_priority": 3}).json()
    r = client.post(f"/templates/{tpl['id']}/create-task")
    assert r.status_code == 201
    assert r.json()["task_source"] == "반복"


def test_top_task():
    client.post("/tasks", json={"title": "낮음", "priority": 1})
    client.post("/tasks", json={"title": "높음", "priority": 5})
    r = client.get("/tasks/top")
    assert r.status_code == 200
    assert r.json()["priority"] == 5


# --- Top Many ---
def test_top_many_default_limit():
    for i in range(5):
        client.post("/tasks", json={"title": f"업무{i}", "priority": i + 1})
    r = client.get("/tasks/top-many")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3  # default limit=3


def test_top_many_custom_limit():
    for i in range(5):
        client.post("/tasks", json={"title": f"업무{i}", "priority": i + 1})
    r = client.get("/tasks/top-many?limit=5")
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_top_many_sorted_by_priority():
    client.post("/tasks", json={"title": "낮음", "priority": 1})
    client.post("/tasks", json={"title": "보통", "priority": 3})
    client.post("/tasks", json={"title": "높음", "priority": 5})
    r = client.get("/tasks/top-many?limit=3")
    items = r.json()
    priorities = [t["priority"] for t in items]
    assert priorities == sorted(priorities, reverse=True)


def test_top_many_excludes_done():
    t = client.post("/tasks", json={"title": "완료된 업무", "priority": 5}).json()
    client.patch(f"/tasks/{t['id']}/status?status=done")
    client.post("/tasks", json={"title": "미완료 업무", "priority": 3})
    r = client.get("/tasks/top-many?limit=5")
    items = r.json()
    assert all(item["status"] != "done" for item in items)


# --- Source Filter ---
def test_source_filter_direct():
    client.post("/tasks", json={"title": "직접 추가"})
    tpl = client.post("/templates", json={"title": "템플릿 업무", "default_priority": 3}).json()
    client.post(f"/templates/{tpl['id']}/create-task")
    r = client.get("/tasks?source=직접")
    items = r.json()
    assert all(t["task_source"] == "직접" for t in items)
    assert len(items) == 1


def test_source_filter_recurring():
    client.post("/tasks", json={"title": "직접 추가"})
    tpl = client.post("/templates", json={"title": "템플릿 업무", "default_priority": 3}).json()
    client.post(f"/templates/{tpl['id']}/create-task")
    r = client.get("/tasks?source=반복")
    items = r.json()
    assert all(t["task_source"] == "반복" for t in items)
    assert len(items) == 1


def test_source_filter_no_filter_returns_all():
    client.post("/tasks", json={"title": "직접 추가"})
    tpl = client.post("/templates", json={"title": "템플릿 업무", "default_priority": 3}).json()
    client.post(f"/templates/{tpl['id']}/create-task")
    r = client.get("/tasks")
    assert len(r.json()) == 2


def test_done_tasks_source_filter():
    t = client.post("/tasks", json={"title": "직접 완료"}).json()
    client.patch(f"/tasks/{t['id']}/status?status=done")
    tpl = client.post("/templates", json={"title": "반복 업무", "default_priority": 3}).json()
    tr = client.post(f"/templates/{tpl['id']}/create-task").json()
    client.patch(f"/tasks/{tr['id']}/status?status=done")

    r_all = client.get("/tasks?filter=done")
    assert len(r_all.json()) == 2

    r_direct = client.get("/tasks?filter=done&source=직접")
    assert len(r_direct.json()) == 1
    assert r_direct.json()[0]["task_source"] == "직접"

    r_recurring = client.get("/tasks?filter=done&source=반복")
    assert len(r_recurring.json()) == 1
    assert r_recurring.json()[0]["task_source"] == "반복"


# --- Clinic name (category as clinic prefix) ---
def test_task_out_includes_category_name():
    cat = client.post("/categories", json={"name": "서울바른치과"}).json()
    t = client.post("/tasks", json={"title": "홈페이지 요청 처리", "category_id": cat["id"]}).json()
    assert t["category_name"] == "서울바른치과"
