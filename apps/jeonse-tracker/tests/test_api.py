import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Base, get_db, User, PreferenceItem, UserWeight
import main as app_module

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app_module.app.dependency_overrides[get_db] = override_get_db
client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestSession()
    users = [User(name="소희"), User(name="지훈")]
    db.add_all(users)
    db.commit()
    items = [
        PreferenceItem(name="고정비용(월 지출)", scope="common", default_weight=5.0),
        PreferenceItem(name="방 넓이", scope="소희", default_weight=4.0),
    ]
    db.add_all(items)
    db.commit()
    for u in db.query(User).all():
        for i in db.query(PreferenceItem).all():
            db.add(UserWeight(user_id=u.id, item_id=i.id, weight=i.default_weight))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_get_users():
    r = client.get("/api/users")
    assert r.status_code == 200
    names = [u["name"] for u in r.json()]
    assert "소희" in names
    assert "지훈" in names


def test_get_items():
    r = client.get("/api/items")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_create_house():
    r = client.post("/api/houses", json={
        "region": "마포구 합정동",
        "deposit": 30000,
        "area": 10.0,
        "status": "관심"
    })
    assert r.status_code == 201
    assert "id" in r.json()


def test_get_houses_sorted():
    r1 = client.post("/api/houses", json={"region": "A동네", "deposit": 20000, "status": "관심"})
    r2 = client.post("/api/houses", json={"region": "B동네", "deposit": 25000, "status": "관심"})
    h1_id = r1.json()["id"]
    h2_id = r2.json()["id"]

    users = client.get("/api/users").json()
    items = client.get("/api/items").json()

    for u in users:
        for it in items:
            client.put(f"/api/houses/{h2_id}/evaluations/{u['id']}/{it['id']}", json={"score": 5})
            client.put(f"/api/houses/{h1_id}/evaluations/{u['id']}/{it['id']}", json={"score": 1})

    houses = client.get("/api/houses").json()
    assert houses[0]["region"] == "B동네"


def test_update_house():
    r = client.post("/api/houses", json={"region": "강남구", "deposit": 50000, "status": "관심"})
    hid = r.json()["id"]
    upd = client.put(f"/api/houses/{hid}", json={"region": "강남구", "deposit": 50000, "status": "방문완료"})
    assert upd.status_code == 200
    detail = client.get(f"/api/houses/{hid}").json()
    assert detail["status"] == "방문완료"


def test_delete_house():
    r = client.post("/api/houses", json={"region": "삭제동네", "deposit": 10000, "status": "제외"})
    hid = r.json()["id"]
    d = client.delete(f"/api/houses/{hid}")
    assert d.status_code == 200
    r2 = client.get(f"/api/houses/{hid}")
    assert r2.status_code == 404


def test_upsert_evaluation():
    r = client.post("/api/houses", json={"region": "평가동네", "deposit": 10000, "status": "관심"})
    hid = r.json()["id"]
    users = client.get("/api/users").json()
    items = client.get("/api/items").json()
    uid = users[0]["id"]
    iid = items[0]["id"]

    ev = client.put(f"/api/houses/{hid}/evaluations/{uid}/{iid}", json={"score": 4})
    assert ev.status_code == 200

    detail = client.get(f"/api/houses/{hid}").json()
    assert detail["evaluations"][str(uid)][str(iid)] == 4


def test_update_weight():
    items = client.get("/api/items").json()
    users = client.get("/api/users").json()
    r = client.put(f"/api/items/{items[0]['id']}/weights/{users[0]['id']}", json={"weight": 2.5})
    assert r.status_code == 200
    items2 = client.get("/api/items").json()
    item = next(i for i in items2 if i["id"] == items[0]["id"])
    assert item["weights"][str(users[0]["id"])] == 2.5
