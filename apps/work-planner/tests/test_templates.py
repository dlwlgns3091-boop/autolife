from datetime import date


def test_create_and_list_template(client):
    res = client.post("/api/templates", json={"title": "일일 보고", "default_priority": 4})
    assert res.status_code == 201
    tmpl = res.json()
    assert tmpl["title"] == "일일 보고"

    lst = client.get("/api/templates").json()
    assert any(t["id"] == tmpl["id"] for t in lst)


def test_apply_template_creates_task(client):
    tmpl = client.post("/api/templates", json={"title": "자동 업무", "default_priority": 3}).json()
    res = client.post(f"/api/templates/{tmpl['id']}/apply")
    assert res.status_code == 201
    task = res.json()
    assert task["title"] == "자동 업무"
    assert task["due_date"] == date.today().isoformat()
    assert task["status"] == "대기"


def test_delete_template(client):
    tmpl = client.post("/api/templates", json={"title": "삭제 템플릿", "default_priority": 2}).json()
    res = client.delete(f"/api/templates/{tmpl['id']}")
    assert res.status_code == 204
    lst = client.get("/api/templates").json()
    assert not any(t["id"] == tmpl["id"] for t in lst)
