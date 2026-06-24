from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean
from .database import Base


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


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
    group = Column(String(10), nullable=False)  # early / mid / late
    is_checked = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)


class ImmediateTask(Base):
    __tablename__ = "immediate_tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    deadline = Column(Date, nullable=True)
    priority = Column(Integer, default=3)  # 1-5
    status = Column(String(20), default="pending")  # pending / in_progress / done
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
