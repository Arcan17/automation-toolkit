"""
APScheduler-based task scheduler.
Loads active ScheduledTask rows from DB and runs them on their cron schedule.
"""

import logging
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.models import Job, ScheduledTask, Notification
from app.database import SessionLocal
from app.services.processor import process_file
from app.services.notifier import send_telegram, send_email, send_whatsapp

logger = logging.getLogger(__name__)

UPLOADS_DIR = Path("uploads")
REPORTS_DIR = Path("reports")

scheduler = AsyncIOScheduler()


async def _run_scheduled_task(task_id: int) -> None:
    db: Session = SessionLocal()
    try:
        task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
        if not task or not task.is_active:
            return

        file_path = UPLOADS_DIR / task.filename
        if not file_path.exists():
            logger.warning(f"Scheduled task {task_id}: file not found {file_path}")
            return

        # Create job record
        job = Job(filename=task.filename, original_name=task.filename, status="processing")
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            stats = process_file(file_path, job.id, REPORTS_DIR)
            job.status = "done"
            job.rows_raw = stats["rows_raw"]
            job.rows_clean = stats["rows_clean"]
            job.duplicates_removed = stats["duplicates_removed"]
            job.nulls_filled = stats["nulls_filled"]
            job.columns = stats["columns"]
            job.report_path = stats["report_path"]
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            logger.error(f"Scheduled task {task_id} failed: {e}")

        from datetime import datetime
        job.finished_at = datetime.utcnow()
        task.last_run = datetime.utcnow()
        db.commit()

        if job.status == "done":
            # Send notifications
            if task.notify_telegram:
                ok = await send_telegram(job.id, task.filename, stats)
                _save_notification(db, job.id, "telegram", ok)
            if task.notify_email and task.notify_target:
                ok = send_email(job.id, task.filename, stats, task.notify_target)
                _save_notification(db, job.id, "email", ok)
            if task.notify_whatsapp and task.notify_target:
                ok = send_whatsapp(job.id, task.filename, stats, task.notify_target)
                _save_notification(db, job.id, "whatsapp", ok)

    finally:
        db.close()


def _save_notification(db: Session, job_id: int, channel: str, success: bool) -> None:
    from datetime import datetime
    notif = Notification(
        job_id=job_id,
        channel=channel,
        status="sent" if success else "failed",
        sent_at=datetime.utcnow() if success else None,
    )
    db.add(notif)
    db.commit()


def load_scheduled_tasks(db: Session) -> None:
    """Load all active scheduled tasks from DB into APScheduler."""
    tasks = db.query(ScheduledTask).filter(ScheduledTask.is_active == True).all()
    for task in tasks:
        try:
            trigger = CronTrigger.from_crontab(task.cron_expr)
            scheduler.add_job(
                _run_scheduled_task,
                trigger=trigger,
                args=[task.id],
                id=f"task_{task.id}",
                replace_existing=True,
            )
            logger.info(f"Scheduled task {task.id} '{task.name}' → {task.cron_expr}")
        except Exception as e:
            logger.error(f"Failed to schedule task {task.id}: {e}")


def start_scheduler(db: Session) -> None:
    load_scheduled_tasks(db)
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
