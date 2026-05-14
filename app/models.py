from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    status = Column(String, default="pending")       # pending / processing / done / failed
    rows_raw = Column(Integer, nullable=True)
    rows_clean = Column(Integer, nullable=True)
    duplicates_removed = Column(Integer, nullable=True)
    nulls_filled = Column(Integer, nullable=True)
    columns = Column(JSON, nullable=True)
    report_path = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)        # file to process
    cron_expr = Column(String, nullable=False)       # e.g. "0 8 * * 1" (every Monday 8am)
    notify_telegram = Column(Boolean, default=False)
    notify_email = Column(Boolean, default=False)
    notify_whatsapp = Column(Boolean, default=False)
    notify_target = Column(String, nullable=True)    # email or phone number
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, nullable=False)
    channel = Column(String, nullable=False)         # telegram / email / whatsapp
    status = Column(String, default="pending")       # sent / failed
    error = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
