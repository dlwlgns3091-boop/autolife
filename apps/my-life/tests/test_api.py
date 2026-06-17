import pytest
from fastapi.testclient import TestClient
from src.database import engine, Base
from src.main import app

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def auth():
    r = client.post("/api/auth/login", json={"password": "testpass"})
    assert r.status_code == 200
    return r.cookies


def test_auth_wrong_password():
    r = client.post("/api/auth/login", json={"password": "wrong"})
    assert r.status_code == 401


def test_auth_status_unauthenticated():
    r = client.get("/api/auth/status")
    assert r.json()["authenticated"] is False


def test_auth_login_logout():
    cookies = auth()
    r = client.get("/api/auth/status", cookies=cookies)
    assert r.json()["authenticated"] is True
    client.post("/api/auth/logout", cookies=cookies)


def test_todo_crud():
    cookies = auth()

    r = client.post("/api/todos", json={"title": "테스트 할일", "priority": 2}, cookies=cookies)
    assert r.status_code == 201
    todo_id = r.json()["id"]

    r = client.get("/api/todos", cookies=cookies)
    assert any(t["id"] == todo_id for t in r.json())

    r = client.put(f"/api/todos/{todo_id}", json={"status": "in_progress"}, cookies=cookies)
    assert r.json()["status"] == "in_progress"

    r = client.delete(f"/api/todos/{todo_id}", cookies=cookies)
    assert r.status_code == 204


def test_todo_requires_auth():
    from fastapi.testclient import TestClient as _TC
    fresh = _TC(app, cookies={})
    r = fresh.get("/api/todos")
    assert r.status_code == 401


def test_budget_category_crud():
    cookies = auth()

    r = client.post("/api/budget/categories", json={"name": "식비"}, cookies=cookies)
    assert r.status_code == 201
    cat_id = r.json()["id"]

    r = client.get("/api/budget/categories", cookies=cookies)
    assert any(c["id"] == cat_id for c in r.json())

    r = client.delete(f"/api/budget/categories/{cat_id}", cookies=cookies)
    assert r.status_code == 204


def test_budget_entry_crud():
    cookies = auth()

    r = client.post("/api/budget/entries", json={
        "date": "2026-06-01", "amount": 15000, "entry_type": "expense", "memo": "점심"
    }, cookies=cookies)
    assert r.status_code == 201
    entry_id = r.json()["id"]

    r = client.get("/api/budget/entries?year=2026&month=6", cookies=cookies)
    assert any(e["id"] == entry_id for e in r.json())

    r = client.put(f"/api/budget/entries/{entry_id}", json={"amount": 20000}, cookies=cookies)
    assert r.json()["amount"] == 20000

    r = client.delete(f"/api/budget/entries/{entry_id}", cookies=cookies)
    assert r.status_code == 204


def test_monthly_summary():
    cookies = auth()
    client.post("/api/budget/entries", json={"date": "2026-06-10", "amount": 500000, "entry_type": "income"}, cookies=cookies)
    client.post("/api/budget/entries", json={"date": "2026-06-10", "amount": 30000, "entry_type": "expense"}, cookies=cookies)

    r = client.get("/api/budget/summary?year=2026&month=6", cookies=cookies)
    s = r.json()
    assert s["total_income"] >= 500000
    assert s["total_expense"] >= 30000
    assert s["balance"] == s["total_income"] - s["total_expense"]


def test_todo_top_requires_auth():
    from fastapi.testclient import TestClient as _TC
    fresh = _TC(app, cookies={})
    r = fresh.get("/api/todos/top")
    assert r.status_code == 401


def test_todo_top_sort_order():
    cookies = auth()
    # Create todos with distinct priorities and due dates
    r1 = client.post("/api/todos", json={"title": "_top_p5_soon", "priority": 5, "due_date": "2027-01-01"}, cookies=cookies)
    r2 = client.post("/api/todos", json={"title": "_top_p5_far", "priority": 5, "due_date": "2027-12-31"}, cookies=cookies)
    r3 = client.post("/api/todos", json={"title": "_top_p3", "priority": 3, "due_date": "2027-06-01"}, cookies=cookies)
    id1, id2, id3 = r1.json()["id"], r2.json()["id"], r3.json()["id"]

    r = client.get("/api/todos/top?count=5", cookies=cookies)
    assert r.status_code == 200
    tops = r.json()
    ids = [t["id"] for t in tops]

    # All three test todos should appear
    assert id1 in ids and id2 in ids and id3 in ids

    # Priority 5 items must come before priority 3 item
    pos1, pos2, pos3 = ids.index(id1), ids.index(id2), ids.index(id3)
    assert pos1 < pos3 and pos2 < pos3

    # Among same priority 5: soonest due (2027-01-01) before later (2027-12-31)
    assert pos1 < pos2

    # cleanup
    for id_ in (id1, id2, id3):
        client.delete(f"/api/todos/{id_}", cookies=cookies)


def test_todo_top_count_param():
    cookies = auth()
    # Create 4 todos
    ids = []
    for i in range(4):
        r = client.post("/api/todos", json={"title": f"_top_count_{i}", "priority": 5}, cookies=cookies)
        ids.append(r.json()["id"])

    r = client.get("/api/todos/top?count=2", cookies=cookies)
    assert r.status_code == 200
    assert len(r.json()) <= 2

    # cleanup
    for id_ in ids:
        client.delete(f"/api/todos/{id_}", cookies=cookies)


def test_todo_top_fewer_than_count():
    cookies = auth()
    # Mark all existing todos as done to isolate this test
    existing = client.get("/api/todos?filter=all", cookies=cookies).json()
    for t in existing:
        client.put(f"/api/todos/{t['id']}", json={"status": "done"}, cookies=cookies)

    r1 = client.post("/api/todos", json={"title": "_few_1", "priority": 5}, cookies=cookies)
    r2 = client.post("/api/todos", json={"title": "_few_2", "priority": 3}, cookies=cookies)
    id1, id2 = r1.json()["id"], r2.json()["id"]

    r = client.get("/api/todos/top?count=5", cookies=cookies)
    assert r.status_code == 200
    tops = r.json()
    top_ids = [t["id"] for t in tops]
    assert id1 in top_ids and id2 in top_ids
    assert len(tops) == 2  # only 2 pending exist

    # cleanup — restore done todos to pending and delete test items
    for t in existing:
        client.put(f"/api/todos/{t['id']}", json={"status": t["status"]}, cookies=cookies)
    for id_ in (id1, id2):
        client.delete(f"/api/todos/{id_}", cookies=cookies)


def test_todo_bulk_create():
    cookies = auth()
    items = [
        {"title": "할일A", "priority": 1, "status": "pending", "due_date": "2026-07-01", "memo": "메모"},
        {"title": "할일B", "priority": 3, "status": "pending", "due_date": None, "memo": None},
        {"title": "할일C", "priority": 5, "status": "pending", "due_date": None, "memo": "테스트"},
    ]
    r = client.post("/api/todos/bulk", json={"items": items}, cookies=cookies)
    assert r.status_code == 201
    assert r.json()["created"] == 3

    r = client.get("/api/todos", cookies=cookies)
    titles = [t["title"] for t in r.json()]
    assert "할일A" in titles
    assert "할일B" in titles
    assert "할일C" in titles


def test_todo_bulk_requires_auth():
    from fastapi.testclient import TestClient as _TC
    fresh = _TC(app, cookies={})
    r = fresh.post("/api/todos/bulk", json={"items": [{"title": "x"}]})
    assert r.status_code == 401


def test_todo_bulk_empty_returns_400():
    cookies = auth()
    r = client.post("/api/todos/bulk", json={"items": []}, cookies=cookies)
    assert r.status_code == 400


def test_budget_bulk_create_with_auto_category():
    cookies = auth()
    items = [
        {"date": "2026-06-15", "amount": 12000, "category_name": "식비_벌크테스트", "entry_type": "expense", "memo": "점심"},
        {"date": "2026-06-16", "amount": 300000, "category_name": None, "entry_type": "income", "memo": "급여"},
        {"date": "2026-06-17", "amount": 5000, "category_name": "교통비_벌크테스트", "entry_type": "expense", "memo": None},
    ]
    r = client.post("/api/budget/bulk", json={"items": items}, cookies=cookies)
    assert r.status_code == 201
    assert r.json()["created"] == 3

    # auto-created category should exist
    cats = client.get("/api/budget/categories", cookies=cookies).json()
    cat_names = [c["name"] for c in cats]
    assert "식비_벌크테스트" in cat_names
    assert "교통비_벌크테스트" in cat_names


def test_budget_bulk_reuses_existing_category():
    cookies = auth()
    # create category first
    client.post("/api/budget/categories", json={"name": "재사용분류_테스트"}, cookies=cookies)
    cats_before = client.get("/api/budget/categories", cookies=cookies).json()
    count_before = len([c for c in cats_before if c["name"] == "재사용분류_테스트"])

    items = [
        {"date": "2026-06-18", "amount": 8000, "category_name": "재사용분류_테스트", "entry_type": "expense", "memo": None},
    ]
    r = client.post("/api/budget/bulk", json={"items": items}, cookies=cookies)
    assert r.status_code == 201

    cats_after = client.get("/api/budget/categories", cookies=cookies).json()
    count_after = len([c for c in cats_after if c["name"] == "재사용분류_테스트"])
    assert count_after == count_before  # no duplicate created


def test_budget_bulk_empty_returns_400():
    cookies = auth()
    r = client.post("/api/budget/bulk", json={"items": []}, cookies=cookies)
    assert r.status_code == 400
