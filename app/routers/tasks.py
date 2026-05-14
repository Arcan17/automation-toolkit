"""
Scheduled tasks routes: CRUD for recurring automation tasks.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ScheduledTask
from app.schemas import TaskCreate, TaskOut, TaskDeactivateResponse
from app.services.scheduler import scheduler
from apscheduler.triggers.cron import CronTrigger

router = APIRouter(prefix="/tasks", tags=["scheduled-tasks"])


@router.post(
    "/",
    response_model=TaskOut,
    summary="Create a scheduled automation task",
    description=(
        "Create a recurring task that runs the full processing pipeline on a cron schedule. "
        "The task will upload, clean, and report the specified file automatically. "
        "Cron examples: `0 8 * * 1` (every Monday 8am), `0 9 * * 1-5` (weekdays 9am), "
        "`0 8 1 * *` (1st of month)."
    ),
)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    try:
        CronTrigger.from_crontab(body.cron_expr)
    except Exception:
        raise HTTPException(400, f"Invalid cron expression: '{body.cron_expr}'")

    task = ScheduledTask(**body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)

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


@router.get(
    "/",
    response_model=List[TaskOut],
    summary="List all scheduled tasks",
    description="Returns all scheduled tasks ordered by most recent first.",
)
def list_tasks(db: Session = Depends(get_db)):
    return db.query(ScheduledTask).order_by(ScheduledTask.created_at.desc()).all()


@router.get(
    "/{task_id}",
    response_model=TaskOut,
    summary="Get a scheduled task by ID",
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task:
        raise HTTPException(404, f"Task {task_id} not found")
    return task


@router.delete(
    "/{task_id}",
    response_model=TaskDeactivateResponse,
    summary="Deactivate a scheduled task",
    description="Marks the task as inactive and removes it from the live scheduler. The record is kept in the database.",
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task:
        raise HTTPException(404, f"Task {task_id} not found")
    task.is_active = False
    db.commit()
    if scheduler.get_job(f"task_{task_id}"):
        scheduler.remove_job(f"task_{task_id}")
    return TaskDeactivateResponse(message=f"Task {task_id} deactivated")
