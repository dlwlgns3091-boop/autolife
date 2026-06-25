from datetime import datetime, timezone, date as date_type
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean
from .database import Base


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Legacy models (kept; tables are never dropped) ─────────────────────────

class Step0Item(Base):
    __tablename__ = "step0_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    memo = Column(Text, nullable=True)
    is_checked = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)


class WeeklyRoutine(Base):
    __tablename__ = "weekly_routines"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    memo = Column(Text, nullable=True)
    is_checked = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)


class MonthlyRoutine(Base):
    __tablename__ = "monthly_routines"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    memo = Column(Text, nullable=True)
    group = Column(String(10), nullable=False)
    is_checked = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)


class ImmediateTask(Base):
    __tablename__ = "immediate_tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    deadline = Column(Date, nullable=True)
    priority = Column(Integer, default=3)
    status = Column(String(20), default="pending")
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


# ── New models ──────────────────────────────────────────────────────────────

class DailyTask(Base):
    __tablename__ = "daily_tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    is_checked = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)


class MonthStartTask(Base):
    __tablename__ = "month_start_tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    is_checked = Column(Boolean, default=False)
    order = Column(Integer, default=0)


class MonthStartHospitalCafe(Base):
    __tablename__ = "month_start_hospitals_cafe"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    is_checked = Column(Boolean, default=False)
    order = Column(Integer, default=0)


class MonthStartHospitalReview(Base):
    __tablename__ = "month_start_hospitals_review"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    is_checked = Column(Boolean, default=False)
    order = Column(Integer, default=0)


class MonthEndTask(Base):
    __tablename__ = "month_end_tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    is_checked = Column(Boolean, default=False)
    order = Column(Integer, default=0)


class WeeklyTask(Base):
    __tablename__ = "weekly_tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    is_checked = Column(Boolean, default=False)
    order = Column(Integer, default=0)


class AlwaysTask(Base):
    __tablename__ = "always_tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    priority = Column(Integer, default=3)
    status = Column(String(20), default="pending")
    memo = Column(Text, nullable=True)
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(Date, nullable=False)
    title = Column(String(200), nullable=False)
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
