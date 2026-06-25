import calendar as cal_mod
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import DailyTask, MonthStartTask, MonthEndTask, WeeklyTask, AlwaysTask
from ..schemas import DashboardOut, DashboardTaskItem, SectionProgress

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _period(day: int, last_day: int) -> str:
    if 1 <= day <= 5:
        return "month_start"
    if day >= 25:
        return "month_end"
    return "normal"


def _progress(items, status_field: bool = False) -> SectionProgress:
    total = len(items)
    if status_field:
        checked = sum(1 for i in items if getattr(i, "status", "") == "done")
    else:
        checked = sum(1 for i in items if getattr(i, "is_checked", False))
    return SectionProgress(total=total, checked=checked)


@router.get("", response_model=DashboardOut)
def get_dashboard(limit: int = Query(5, ge=0), db: Session = Depends(get_db)):
    today = date.today()
    last_day = cal_mod.monthrange(today.year, today.month)[1]
    period = _period(today.day, last_day)

    daily_items = db.query(DailyTask).order_by(DailyTask.order, DailyTask.id).all()
    ms_tasks = db.query(MonthStartTask).order_by(MonthStartTask.order, MonthStartTask.id).all()
    me_tasks = db.query(MonthEndTask).order_by(MonthEndTask.order, MonthEndTask.id).all()
    weekly_items = db.query(WeeklyTask).order_by(WeeklyTask.order, WeeklyTask.id).all()
    always_items = db.query(AlwaysTask).order_by(AlwaysTask.priority.desc(), AlwaysTask.id).all()

    dashboard_items: List[DashboardTaskItem] = []

    for it in daily_items:
        if not it.is_checked:
            dashboard_items.append(DashboardTaskItem(
                id=it.id, type="daily", title=it.title, is_urgent=False,
            ))

    if period == "month_start":
        for it in ms_tasks:
            if not it.is_checked:
                dashboard_items.append(DashboardTaskItem(
                    id=it.id, type="month_start", title=it.title, is_urgent=True,
                ))

    if period == "month_end":
        for it in me_tasks:
            if not it.is_checked:
                dashboard_items.append(DashboardTaskItem(
                    id=it.id, type="month_end", title=it.title, is_urgent=True,
                ))

    for it in weekly_items:
        if not it.is_checked:
            dashboard_items.append(DashboardTaskItem(
                id=it.id, type="weekly", title=it.title, is_urgent=False,
            ))

    for it in always_items:
        if it.status != "done":
            is_urgent = bool(
                it.priority >= 4
                or (it.deadline is not None and (it.deadline - today).days <= 3)
            )
            dashboard_items.append(DashboardTaskItem(
                id=it.id, type="always", title=it.title, is_urgent=is_urgent,
                deadline=it.deadline, priority=it.priority, status=it.status,
            ))

    always_progress = _progress(always_items, status_field=True)

    if limit > 0:
        dashboard_items = dashboard_items[:limit]

    return DashboardOut(
        today=today.isoformat(),
        current_period=period,
        daily=_progress(daily_items),
        month_start=_progress(ms_tasks),
        month_end=_progress(me_tasks),
        weekly=_progress(weekly_items),
        always=always_progress,
        items=dashboard_items,
    )
