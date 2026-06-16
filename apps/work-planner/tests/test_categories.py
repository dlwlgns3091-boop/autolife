def test_create_and_list_category(client):
    res = client.post("/api/categories", json={"name": "영업"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "영업"
    assert "id" in data

    res2 = client.get("/api/categories")
    assert res2.status_code == 200
    assert any(c["name"] == "영업" for c in res2.json())


def test_duplicate_category_rejected(client):
    client.post("/api/categories", json={"name": "중복"})
    res = client.post("/api/categories", json={"name": "중복"})
    assert res.status_code == 400


def test_update_category(client):
    cat = client.post("/api/categories", json={"name": "구형"}).json()
    res = client.put(f"/api/categories/{cat['id']}", json={"name": "신형"})
    assert res.status_code == 200
    assert res.json()["name"] == "신형"


def test_delete_category(client):
    cat = client.post("/api/categories", json={"name": "삭제용"}).json()
    res = client.delete(f"/api/categories/{cat['id']}")
    assert res.status_code == 204
    cats = client.get("/api/categories").json()
    assert not any(c["id"] == cat["id"] for c in cats)
