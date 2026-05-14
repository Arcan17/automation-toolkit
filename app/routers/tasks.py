"""
Scheduled tasks routes: CRUD for recurring automation tasks.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import ScheduledTask
from app.services.scheduler import scheduler
from apscheduler.triggers.cron import CronTrigger

router = APIRouter(prefix="/tasks", tags=["scheduled-tasks"])


class TaskCreate(BaseModel):
    name: str
    filename: str
    cron_expr: str
    notify_telegram: bool = False
    notify_email: bool = False
    notify_whatsapp: bool = False
    notify_target: Optional[str] = None


@router.post("/")
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    # Validate cron expression
    try:
        CronTrigger.from_crontab(body.cron_expr)
    except Exception:
        raise HTTPException(400, f"Invalid cron expression: '{body.cron_expr}'")

    task = ScheduledTask(**body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)

    # Register in live scheduler
    from app.services.scheduler import _run_scheduled_task
    trigger = CronTrigger.from_crontab(task.cron_expr)
    scheduler.add_job(
        _run_scheduled_task,
        trigger=trigger,
        args=[task.id],
        id=f"task_{task.id}",
        replace_existing=True,
    )
    return task


@router.get("/")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(ScheduledTask).order_by(ScheduledTask.created_at.desc()).all()


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    task.is_active = False
    db.commit()
    if scheduler.get_job(f"task_{task_id}"):
        scheduler.remove_job(f"task_{task_id}")
    return {"message": f"Task {task_id} deactivated"}
