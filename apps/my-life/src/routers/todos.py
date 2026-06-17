from datetime import date
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Todo
from ..schemas import TodoCreate, TodoUpdate, TodoOut
from ..auth import require_auth

router = APIRouter(prefix="/api/todos", tags=["todos"])


def _query_sorted(db: Session):
    return (
        db.query(Todo)
        .order_by(Todo.priority.asc(), Todo.due_date.asc().nulls_last(), Todo.created_at.desc())
    )


@router.get("", response_model=list[TodoOut])
def list_todos(
    request: Request,
    filter: str = "all",  # all / today / week / done
    db: Session = Depends(get_db),
):
    require_auth(request)
    today = date.today()
    q = _query_sorted(db)
    if filter == "done":
        q = q.filter(Todo.status == "done")
    elif filter == "today":
        q = q.filter(Todo.status != "done", Todo.due_date == today)
    elif filter == "week":
        from datetime import timedelta
        week_end = today + timedelta(days=6)
        q = q.filter(Todo.status != "done", Todo.due_date <= week_end)
    else:
        q = q.filter(Todo.status != "done")
    return q.all()


@router.post("", response_model=TodoOut, status_code=201)
def create_todo(request: Request, body: TodoCreate, db: Session = Depends(get_db)):
    require_auth(request)
    todo = Todo(**body.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.put("/{todo_id}", response_model=TodoOut)
def update_todo(request: Request, todo_id: int, body: TodoUpdate, db: Session = Depends(get_db)):
    require_auth(request)
    todo = db.get(Todo, todo_id)
    if not todo:
        raise HTTPException(404, "Not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(todo, k, v)
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    require_auth(request)
    todo = db.get(Todo, todo_id)
    if not todo:
        raise HTTPException(404, "Not found")
    db.delete(todo)
    db.commit()
