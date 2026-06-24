from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Step0Item, WeeklyRoutine, MonthlyRoutine, ImmediateTask
from ..schemas import DashboardOut, DashboardItem, DashboardSection

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _current_period(today: date) -> str:
    if today.day <= 10:
        return "early"
    elif today.day <= 20:
        return "mid"
    return "late"


@router.get("", response_model=DashboardOut)
def get_dashboard(limit: int = Query(default=5, ge=0), db: Session = Depends(get_db)):
    today = date.today()
    period = _current_period(today)

    step0_total = db.query(Step0Item).count()
    step0_checked = db.query(Step0Item).filter(Step0Item.is_checked == True).count()

    weekly_total = db.query(WeeklyRoutine).count()
    weekly_checked = db.query(WeeklyRoutine).filter(WeeklyRoutine.is_checked == True).count()

    monthly_total = db.query(MonthlyRoutine).count()
    monthly_checked = db.query(MonthlyRoutine).filter(MonthlyRoutine.is_checked == True).count()

    imm_done = db.query(ImmediateTask).filter(ImmediateTask.status == "done").count()
    imm_pending = db.query(ImmediateTask).filter(ImmediateTask.status != "done").count()
    imm_all = imm_done + imm_pending

    items: list[DashboardItem] = []

    for t in db.query(ImmediateTask).filter(
        ImmediateTask.status != "done"
    ).order_by(ImmediateTask.priority.desc(), ImmediateTask.deadline.asc()).all():
        is_urgent = t.deadline is not None and t.deadline <= today
        items.append(DashboardItem(
            id=t.id, type="immediate", title=t.title, is_urgent=is_urgent,
            deadline=t.deadline, priority=t.priority, status=t.status,
        ))

    for r in db.query(WeeklyRoutine).filter(
        WeeklyRoutine.is_checked == False
    ).order_by(WeeklyRoutine.order, WeeklyRoutine.id).all():
        items.append(DashboardItem(id=r.id, type="weekly", title=r.title, is_urgent=False))

    for r in db.query(MonthlyRoutine).filter(
        MonthlyRoutine.group == period,
        MonthlyRoutine.is_checked == False,
    ).order_by(MonthlyRoutine.order, MonthlyRoutine.id).all():
        items.append(DashboardItem(id=r.id, type="monthly", title=r.title, is_urgent=False, group=period))

    for r in db.query(Step0Item).filter(
        Step0Item.is_checked == False
    ).order_by(Step0Item.order, Step0Item.id).all():
        items.append(DashboardItem(id=r.id, type="step0", title=r.title, is_urgent=False))

    if limit > 0:
        items = items[:limit]

    return DashboardOut(
        items=items,
        step0=DashboardSection(total=step0_total, checked=step0_checked),
        weekly=DashboardSection(total=weekly_total, checked=weekly_checked),
        monthly=DashboardSection(total=monthly_total, checked=monthly_checked),
        immediate=DashboardSection(total=imm_all, checked=imm_done),
        current_period=period,
    )
