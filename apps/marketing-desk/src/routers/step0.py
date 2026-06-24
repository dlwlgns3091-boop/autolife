from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Step0Item
from ..schemas import Step0ItemCreate, Step0ItemUpdate, Step0ItemOut

router = APIRouter(prefix="/step0", tags=["step0"])


@router.get("", response_model=list[Step0ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(Step0Item).order_by(Step0Item.order, Step0Item.id).all()


@router.post("", response_model=Step0ItemOut, status_code=201)
def create_item(data: Step0ItemCreate, db: Session = Depends(get_db)):
    item = Step0Item(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=Step0ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Step0Item, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    return item


@router.put("/{item_id}", response_model=Step0ItemOut)
def update_item(item_id: int, data: Step0ItemUpdate, db: Session = Depends(get_db)):
    item = db.get(Step0Item, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}/check", response_model=Step0ItemOut)
def toggle_check(item_id: int, checked: bool = Query(...), db: Session = Depends(get_db)):
    item = db.get(Step0Item, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    item.is_checked = checked
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Step0Item, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()
