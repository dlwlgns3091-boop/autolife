from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ImmediateTask
from ..schemas import ImmediateTaskCreate, ImmediateTaskUpdate, ImmediateTaskOut

router = APIRouter(prefix="/immediate", tags=["immediate"])


@router.get("", response_model=list[ImmediateTaskOut])
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(ImmediateTask).all()
    # Sort: undone first (priority desc, deadline asc nulls last), done last
    def sort_key(t):
        is_done = 1 if t.status == "done" else 0
        deadline_val = t.deadline.isoformat() if t.deadline else "9999-12-31"
        return (is_done, -t.priority, deadline_val)
    return sorted(tasks, key=sort_key)


@router.post("", response_model=ImmediateTaskOut, status_code=status.HTTP_201_CREATED)
def create_task(body: ImmediateTaskCreate, db: Session = Depends(get_db)):
    task = ImmediateTask(**body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=ImmediateTaskOut)
def update_task(task_id: int, body: ImmediateTaskUpdate, db: Session = Depends(get_db)):
    task = db.get(ImmediateTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(ImmediateTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
