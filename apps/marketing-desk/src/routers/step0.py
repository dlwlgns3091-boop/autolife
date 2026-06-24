from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Step0Item
from ..schemas import Step0ItemCreate, Step0ItemUpdate, Step0ItemOut

router = APIRouter(prefix="/step0", tags=["step0"])


@router.get("", response_model=list[Step0ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(Step0Item).order_by(Step0Item.sort_order, Step0Item.id).all()


@router.post("", response_model=Step0ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(body: Step0ItemCreate, db: Session = Depends(get_db)):
    max_order = db.query(Step0Item).count()
    item = Step0Item(**body.model_dump(), sort_order=max_order)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=Step0ItemOut)
def update_item(item_id: int, body: Step0ItemUpdate, db: Session = Depends(get_db)):
    item = db.get(Step0Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Step0Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()


@router.patch("/{item_id}/check", response_model=Step0ItemOut)
def toggle_check(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Step0Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.checked = not item.checked
    db.commit()
    db.refresh(item)
    return item
