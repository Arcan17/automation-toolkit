"""
Job routes: upload file, process, get status, download report.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, Notification
from app.services.notifier import send_email, send_telegram, send_whatsapp
from app.services.processor import process_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])

UPLOADS_DIR = Path("uploads")
REPORTS_DIR = Path("reports")
UPLOADS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_and_process(
    file: UploadFile = File(...),
    notify_telegram: bool = Form(False),
    notify_email: bool = Form(False),
    notify_whatsapp: bool = Form(False),
    notify_target: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a CSV/Excel file, process it, and optionally send notifications."""
    allowed = {".csv", ".xlsx", ".xls"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, f"Unsupported file type: {suffix}. Use CSV or Excel.")

    # Save uploaded file
    dest = UPLOADS_DIR / file.filename
    content = await file.read()
    dest.write_bytes(content)

    # Create job
    job = Job(filename=file.filename, original_name=file.filename, status="processing")
    db.add(job)
    db.commit()
    db.refresh(job)

    # Process in background
    asyncio.create_task(
        _process_and_notify(
            job.id, dest, notify_telegram, notify_email, notify_whatsapp, notify_target
        )
    )

    return {"job_id": job.id, "status": "processing", "filename": file.filename}


async def _process_and_notify(
    job_id: int,
    file_path: Path,
    notify_telegram: bool,
    notify_email: bool,
    notify_whatsapp: bool,
    notify_target: Optional[str],
) -> None:
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        try:
            stats = process_file(file_path, job_id, REPORTS_DIR)
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
            logger.error(f"Job {job_id} failed: {e}")
            db.commit()
            return

        job.finished_at = datetime.utcnow()
        db.commit()

        # Notifications
        if notify_telegram:
            ok = await send_telegram(job_id, file_path.name, stats)
            _save_notif(db, job_id, "telegram", ok)
        if notify_email and notify_target:
            ok = send_email(job_id, file_path.name, stats, notify_target)
            _save_notif(db, job_id, "email", ok)
        if notify_whatsapp and notify_target:
            ok = send_whatsapp(job_id, file_path.name, stats, notify_target)
            _save_notif(db, job_id, "whatsapp", ok)

    finally:
        db.close()


def _save_notif(db, job_id: int, channel: str, success: bool) -> None:
    notif = Notification(
        job_id=job_id,
        channel=channel,
        status="sent" if success else "failed",
        sent_at=datetime.utcnow() if success else None,
    )
    db.add(notif)
    db.commit()


@router.get("/")
def list_jobs(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.get("/{job_id}/download")
def download_report(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or not job.report_path:
        raise HTTPException(404, "Report not found")
    path = Path(job.report_path)
    if not path.exists():
        raise HTTPException(404, "Report file not found on disk")
    return FileResponse(path, filename=path.name, media_type="application/octet-stream")
