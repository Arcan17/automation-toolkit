"""
Job routes: upload file, process, get status, download report.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, Notification
from app.schemas import JobOut, JobUploadResponse
from app.services.notifier import send_email, send_telegram, send_whatsapp
from app.services.processor import process_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])

UPLOADS_DIR = Path("uploads")
REPORTS_DIR = Path("reports")
UPLOADS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_SIZE_MB = 10


@router.post(
    "/upload",
    response_model=JobUploadResponse,
    summary="Upload and process a CSV or Excel file",
    description=(
        "Upload a CSV or Excel file. The file is processed asynchronously: "
        "duplicates are removed, missing values are filled, and a clean Excel report is generated. "
        "Poll `GET /jobs/{job_id}` until `status` is `done` or `failed`, "
        "then download the report from `GET /jobs/{job_id}/download`."
    ),
)
async def upload_and_process(
    file: UploadFile = File(..., description="CSV (.csv) or Excel (.xlsx / .xls) file"),
    notify_telegram: bool = Form(False, description="Send a Telegram alert when done"),
    notify_email: bool = Form(False, description="Send an email alert when done"),
    notify_whatsapp: bool = Form(False, description="Send a WhatsApp alert when done"),
    notify_target: Optional[str] = Form(None, description="Email address or phone number for alerts"),
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Unsupported file type '{suffix}'. Accepted: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(413, f"File too large ({size_mb:.1f} MB). Maximum is {MAX_SIZE_MB} MB.")

    dest = UPLOADS_DIR / file.filename
    dest.write_bytes(content)

    job = Job(filename=file.filename, original_name=file.filename, status="processing")
    db.add(job)
    db.commit()
    db.refresh(job)

    asyncio.create_task(
        _process_and_notify(
            job.id, dest, notify_telegram, notify_email, notify_whatsapp, notify_target
        )
    )

    return JobUploadResponse(job_id=job.id, status="processing", filename=file.filename)


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


@router.get(
    "/",
    response_model=List[JobOut],
    summary="List all processing jobs",
    description="Returns all jobs ordered by most recent first. Each job includes processing stats and status.",
)
def list_jobs(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


@router.get(
    "/{job_id}",
    response_model=JobOut,
    summary="Get job status and stats",
    description=(
        "Returns full details for a single job. "
        "Poll this endpoint after upload until `status` is `done` or `failed`."
    ),
)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")
    return job


@router.get(
    "/{job_id}/download",
    summary="Download the Excel report",
    description=(
        "Download the cleaned Excel report for a completed job. "
        "The file has two sheets: **Summary** (stats overview) and **Clean Data** (processed rows)."
    ),
    tags=["jobs"],
)
def download_report(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")
    if not job.report_path:
        raise HTTPException(404, "No report available — job may still be processing or failed")
    path = Path(job.report_path)
    if not path.exists():
        raise HTTPException(404, "Report file not found on disk")
    return FileResponse(
        path,
        filename=f"cleaned_{job.original_name.rsplit('.', 1)[0]}_job{job_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
