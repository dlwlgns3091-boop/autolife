from datetime import date, timedelta


def _task(client, **kwargs):
    payload = {"title": "테스트 업무", "priority": 3, **kwargs}
    return client.post("/api/tasks", json=payload).json()


def test_create_and_list_task(client):
    t = _task(client)
    assert t["title"] == "테스트 업무"
    assert t["status"] == "대기"

    res = client.get("/api/tasks")
    assert any(x["id"] == t["id"] for x in res.json())


def test_task_with_category(client):
    cat = client.post("/api/categories", json={"name": "행정"}).json()
    t = _task(client, category_id=cat["id"])
    assert t["category"]["name"] == "행정"


def test_update_task(client):
    t = _task(client)
    res = client.patch(f"/api/tasks/{t['id']}", json={"status": "진행중", "priority": 5})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "진행중"
    assert data["priority"] == 5


def test_delete_task(client):
    t = _task(client)
    res = client.delete(f"/api/tasks/{t['id']}")
    assert res.status_code == 204


def test_filter_by_status(client):
    _task(client, title="대기 업무", status="대기")
    _task(client, title="완료 업무", status="완료")
    res = client.get("/api/tasks?status=완료").json()
    assert all(t["status"] == "완료" for t in res)


def test_incomplete_filter(client):
    _task(client, title="대기")
    _task(client, title="완료", status="완료")
    res = client.get("/api/tasks?status=incomplete").json()
    assert all(t["status"] != "완료" for t in res)


def test_sorting_priority_then_due_date(client):
    today_str = date.today().isoformat()
    tmr = (date.today() + timedelta(days=1)).isoformat()
    _task(client, title="낮은 우선순위", priority=1, due_date=today_str)
    _task(client, title="높은 우선순위", priority=5, due_date=tmr)
    tasks = client.get("/api/tasks?status=incomplete").json()
    assert tasks[0]["title"] == "높은 우선순위"


def test_summary(client):
    today_str = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    _task(client, title="오늘 마감", due_date=today_str)
    _task(client, title="기한 초과", due_date=yesterday)
    _task(client, title="진행중", status="진행중")
    res = client.get("/api/tasks/summary").json()
    assert res["today_count"] >= 1
    assert res["overdue_count"] >= 1
    assert res["in_progress_count"] >= 1
