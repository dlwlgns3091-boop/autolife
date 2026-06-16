from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Task, TaskTemplate
from ..schemas import TaskTemplateCreate, TaskTemplateUpdate, TaskTemplateOut, TaskOut

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=List[TaskTemplateOut])
def list_templates(db: Session = Depends(get_db)):
    return db.query(TaskTemplate).order_by(TaskTemplate.id).all()


@router.post("", response_model=TaskTemplateOut, status_code=201)
def create_template(body: TaskTemplateCreate, db: Session = Depends(get_db)):
    tmpl = TaskTemplate(**body.model_dump())
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return tmpl


@router.put("/{template_id}", response_model=TaskTemplateOut)
def update_template(template_id: int, body: TaskTemplateUpdate, db: Session = Depends(get_db)):
    tmpl = db.get(TaskTemplate, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다.")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(tmpl, field, value)
    db.commit()
    db.refresh(tmpl)
    return tmpl


@router.delete("/{template_id}", status_code=204)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    tmpl = db.get(TaskTemplate, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다.")
    db.delete(tmpl)
    db.commit()


@router.post("/{template_id}/apply", response_model=TaskOut, status_code=201)
def apply_template(template_id: int, db: Session = Depends(get_db)):
    """템플릿을 클릭 한 번으로 오늘 날짜 업무로 즉시 생성"""
    tmpl = db.get(TaskTemplate, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다.")
    task = Task(
        title=tmpl.title,
        category_id=tmpl.category_id,
        priority=tmpl.default_priority,
        due_date=date.today(),
        status="대기",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
