from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os

from database import get_db, init_db, User, PreferenceItem, UserWeight, House, Evaluation

app = FastAPI(title="전세집 트래커")

# Initialize DB on startup
@app.on_event("startup")
def startup():
    init_db()

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    return FileResponse(os.path.join(static_dir, "index.html"))


# ── Schemas ──────────────────────────────────────────────────────────────────

class HouseCreate(BaseModel):
    region: str
    deposit: int
    area: Optional[float] = None
    rooms: Optional[int] = None
    bathrooms: Optional[int] = None
    monthly_cost: Optional[int] = None
    link: Optional[str] = None
    memo: Optional[str] = None
    status: Optional[str] = "관심"

class HouseUpdate(HouseCreate):
    pass

class WeightUpdate(BaseModel):
    weight: float

class EvaluationUpsert(BaseModel):
    score: float  # 1~5


# ── Users ─────────────────────────────────────────────────────────────────────

@app.get("/api/users")
def get_users(db: Session = Depends(get_db)):
    return [{"id": u.id, "name": u.name} for u in db.query(User).all()]


# ── Preference Items & Weights ────────────────────────────────────────────────

@app.get("/api/items")
def get_items(db: Session = Depends(get_db)):
    items = db.query(PreferenceItem).all()
    users = db.query(User).all()
    result = []
    for item in items:
        weights = {}
        for uw in item.weights:
            weights[uw.user_id] = uw.weight
        result.append({
            "id": item.id,
            "name": item.name,
            "scope": item.scope,
            "default_weight": item.default_weight,
            "weights": weights,
        })
    return result


@app.put("/api/items/{item_id}/weights/{user_id}")
def update_weight(item_id: int, user_id: int, body: WeightUpdate, db: Session = Depends(get_db)):
    uw = db.query(UserWeight).filter_by(item_id=item_id, user_id=user_id).first()
    if not uw:
        raise HTTPException(status_code=404, detail="Weight not found")
    uw.weight = body.weight
    db.commit()
    return {"ok": True}


# ── Houses ────────────────────────────────────────────────────────────────────

def _score_for_house(house: House, db: Session):
    users = db.query(User).all()
    items = db.query(PreferenceItem).all()
    scores_by_user = {}
    for user in users:
        total = 0.0
        for item in items:
            ev = db.query(Evaluation).filter_by(house_id=house.id, user_id=user.id, item_id=item.id).first()
            sc = ev.score if ev else 0.0
            uw = db.query(UserWeight).filter_by(user_id=user.id, item_id=item.id).first()
            w = uw.weight if uw else item.default_weight
            total += sc * w
        scores_by_user[user.id] = round(total, 2)
    combined = round(sum(scores_by_user.values()), 2)
    return scores_by_user, combined


@app.get("/api/houses")
def get_houses(db: Session = Depends(get_db)):
    houses = db.query(House).all()
    result = []
    for h in houses:
        scores_by_user, combined = _score_for_house(h, db)
        result.append({
            "id": h.id,
            "region": h.region,
            "deposit": h.deposit,
            "area": h.area,
            "rooms": h.rooms,
            "bathrooms": h.bathrooms,
            "monthly_cost": h.monthly_cost,
            "link": h.link,
            "memo": h.memo,
            "status": h.status,
            "scores": scores_by_user,
            "combined_score": combined,
        })
    result.sort(key=lambda x: x["combined_score"], reverse=True)
    return result


@app.post("/api/houses", status_code=201)
def create_house(body: HouseCreate, db: Session = Depends(get_db)):
    h = House(**body.model_dump())
    db.add(h)
    db.commit()
    db.refresh(h)
    return {"id": h.id}


@app.put("/api/houses/{house_id}")
def update_house(house_id: int, body: HouseUpdate, db: Session = Depends(get_db)):
    h = db.query(House).get(house_id)
    if not h:
        raise HTTPException(status_code=404, detail="House not found")
    for k, v in body.model_dump().items():
        setattr(h, k, v)
    db.commit()
    return {"ok": True}


@app.delete("/api/houses/{house_id}")
def delete_house(house_id: int, db: Session = Depends(get_db)):
    h = db.query(House).get(house_id)
    if not h:
        raise HTTPException(status_code=404, detail="House not found")
    db.query(Evaluation).filter_by(house_id=house_id).delete()
    db.delete(h)
    db.commit()
    return {"ok": True}


@app.get("/api/houses/{house_id}")
def get_house(house_id: int, db: Session = Depends(get_db)):
    h = db.query(House).get(house_id)
    if not h:
        raise HTTPException(status_code=404, detail="House not found")
    users = db.query(User).all()
    items = db.query(PreferenceItem).all()
    evaluations = {}
    for user in users:
        evaluations[user.id] = {}
        for item in items:
            ev = db.query(Evaluation).filter_by(house_id=house_id, user_id=user.id, item_id=item.id).first()
            evaluations[user.id][item.id] = ev.score if ev else 0
    scores_by_user, combined = _score_for_house(h, db)
    return {
        "id": h.id,
        "region": h.region,
        "deposit": h.deposit,
        "area": h.area,
        "rooms": h.rooms,
        "bathrooms": h.bathrooms,
        "monthly_cost": h.monthly_cost,
        "link": h.link,
        "memo": h.memo,
        "status": h.status,
        "evaluations": evaluations,
        "scores": scores_by_user,
        "combined_score": combined,
    }


# ── Evaluations ───────────────────────────────────────────────────────────────

@app.put("/api/houses/{house_id}/evaluations/{user_id}/{item_id}")
def upsert_evaluation(house_id: int, user_id: int, item_id: int, body: EvaluationUpsert, db: Session = Depends(get_db)):
    ev = db.query(Evaluation).filter_by(house_id=house_id, user_id=user_id, item_id=item_id).first()
    if ev:
        ev.score = body.score
    else:
        db.add(Evaluation(house_id=house_id, user_id=user_id, item_id=item_id, score=body.score))
    db.commit()
    return {"ok": True}
