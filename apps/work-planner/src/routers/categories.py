from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import TaskCategory
from ..schemas import TaskCategoryCreate, TaskCategoryUpdate, TaskCategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[TaskCategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(TaskCategory).order_by(TaskCategory.name).all()


@router.post("", response_model=TaskCategoryOut, status_code=201)
def create_category(body: TaskCategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(TaskCategory).filter(TaskCategory.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="같은 이름의 업무 종류가 이미 존재합니다.")
    cat = TaskCategory(name=body.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{category_id}", response_model=TaskCategoryOut)
def update_category(category_id: int, body: TaskCategoryUpdate, db: Session = Depends(get_db)):
    cat = db.get(TaskCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="업무 종류를 찾을 수 없습니다.")
    cat.name = body.name
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.get(TaskCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="업무 종류를 찾을 수 없습니다.")
    db.delete(cat)
    db.commit()
