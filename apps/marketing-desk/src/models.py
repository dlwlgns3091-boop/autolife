from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Integer, String, Date, DateTime, Text
from .database import Base


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Step0Item(Base):
    __tablename__ = "step0_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    memo = Column(Text, nullable=True)
    checked = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class WeeklyItem(Base):
    __tablename__ = "weekly_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    memo = Column(Text, nullable=True)
    checked = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class MonthlyItem(Base):
    __tablename__ = "monthly_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    memo = Column(Text, nullable=True)
    checked = Column(Boolean, default=False, nullable=False)
    period = Column(String(10), nullable=False)  # 월초 / 월중 / 월말
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


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
