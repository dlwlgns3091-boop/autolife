from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import TaskTemplate, TaskCategory, Task
from ..schemas import TemplateCreate, TemplateUpdate, TemplateOut, TaskOut

router = APIRouter(prefix="/templates", tags=["templates"])


def _tpl_out(t: TaskTemplate) -> TemplateOut:
    return TemplateOut(
        id=t.id,
        title=t.title,
        category_id=t.category_id,
        category_name=t.category.name if t.category else None,
        default_priority=t.default_priority,
        deadline_offset_days=t.deadline_offset_days,
    )


def _task_out_from_task(t: Task) -> TaskOut:
    from ..schemas import TaskOut as TO
    return TO(
        id=t.id,
        title=t.title,
        category_id=t.category_id,
        category_name=t.category.name if t.category else None,
        priority=t.priority,
        status=t.status,
        deadline=t.deadline,
        recurrence=t.recurrence,
        memo=t.memo,
        source=t.source or "반복",
    )


@router.get("", response_model=list[TemplateOut])
def list_templates(db: Session = Depends(get_db)):
    return [_tpl_out(t) for t in db.query(TaskTemplate).order_by(TaskTemplate.id).all()]


@router.post("", response_model=TemplateOut, status_code=201)
def create_template(data: TemplateCreate, db: Session = Depends(get_db)):
    if data.category_id and not db.get(TaskCategory, data.category_id):
        raise HTTPException(404, "Category not found")
    tpl = TaskTemplate(**data.model_dump())
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return _tpl_out(tpl)


@router.put("/{tpl_id}", response_model=TemplateOut)
def update_template(tpl_id: int, data: TemplateUpdate, db: Session = Depends(get_db)):
    tpl = db.get(TaskTemplate, tpl_id)
    if not tpl:
        raise HTTPException(404, "Template not found")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(tpl, field, val)
    db.commit()
    db.refresh(tpl)
    return _tpl_out(tpl)


@router.delete("/{tpl_id}", status_code=204)
def delete_template(tpl_id: int, db: Session = Depends(get_db)):
    tpl = db.get(TaskTemplate, tpl_id)
    if not tpl:
        raise HTTPException(404, "Template not found")
    db.delete(tpl)
    db.commit()


@router.post("/{tpl_id}/create-task", response_model=TaskOut, status_code=201)
def create_task_from_template(tpl_id: int, db: Session = Depends(get_db)):
    tpl = db.get(TaskTemplate, tpl_id)
    if not tpl:
        raise HTTPException(404, "Template not found")
    today = date.today()
    deadline = today + timedelta(days=tpl.deadline_offset_days) if tpl.deadline_offset_days is not None else None
    task = Task(
        title=tpl.title,
        category_id=tpl.category_id,
        priority=tpl.default_priority,
        deadline=deadline,
        status="pending",
        source="반복",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_out_from_task(task)
