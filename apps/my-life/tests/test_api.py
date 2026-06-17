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
