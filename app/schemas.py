"""
Pydantic response schemas for FastAPI endpoints.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


# ── Job schemas ───────────────────────────────────────────────────────────────

class JobUploadResponse(BaseModel):
    job_id: int
    status: str
    filename: str


class JobOut(BaseModel):
    id: int
    filename: str
    original_name: str
    status: str
    rows_raw: Optional[int] = None
    rows_clean: Optional[int] = None
    duplicates_removed: Optional[int] = None
    nulls_filled: Optional[int] = None
    columns: Optional[Any] = None
    report_path: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ── Task schemas ──────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    name: str
    filename: str
    cron_expr: str
    notify_telegram: bool = False
    notify_email: bool = False
    notify_whatsapp: bool = False
    notify_target: Optional[str] = None


class TaskOut(BaseModel):
    id: int
    name: str
    filename: str
    cron_expr: str
    notify_telegram: bool
    notify_email: bool
    notify_whatsapp: bool
    notify_target: Optional[str] = None
    is_active: bool
    last_run: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskDeactivateResponse(BaseModel):
    message: str


# ── Health schema ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    scheduler: str
    database: str
