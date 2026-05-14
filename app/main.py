import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import get_db, init_db
from app.routers import jobs, tasks
from app.schemas import HealthResponse
from app.services.scheduler import scheduler, start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── API metadata ──────────────────────────────────────────────────────────────
tags_metadata = [
    {
        "name": "jobs",
        "description": (
            "Upload CSV/Excel files for automated processing. "
            "Each job cleans the data, removes duplicates, fills missing values, "
            "and generates a downloadable Excel report."
        ),
    },
    {
        "name": "scheduled-tasks",
        "description": (
            "Create recurring automation tasks with cron expressions. "
            "Tasks run the full processing pipeline automatically and can send "
            "alerts via Telegram, Email or WhatsApp."
        ),
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    db = next(get_db())
    start_scheduler(db)
    yield
    stop_scheduler()
    logger.info("Scheduler stopped")


app = FastAPI(
    title="Automation Toolkit API",
    description="""
## Automation Toolkit

A full-stack data automation platform that processes CSV/Excel files, cleans data,
generates downloadable reports, and sends multi-channel alerts.

### What it does
- **Upload** CSV or Excel files (up to 10 MB)
- **Clean** data: remove duplicates, strip whitespace, fill missing values
- **Report** Generate a formatted Excel report with a Summary sheet and Clean Data sheet
- **Alert** Send processing results via Telegram, Email (SMTP), or WhatsApp (Twilio)
- **Schedule** Run processing jobs automatically with cron expressions

### Quick start
1. `POST /jobs/upload` — upload a CSV/Excel file
2. `GET /jobs/{id}` — poll until status is `done`
3. `GET /jobs/{id}/download` — download the clean Excel report

### Demo
Try uploading `sample_demo.csv` from the project root — it includes duplicates and missing values.
""",
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    contact={
        "name": "Bastian Altamirano",
        "url": "https://github.com/Arcan17",
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(tasks.router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health():
    """Health check. Returns API status, scheduler state, and database connectivity."""
    db_ok = "ok"
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db.close()
    except Exception:
        db_ok = "error"

    return HealthResponse(
        status="ok",
        version="1.0.0",
        scheduler="running" if scheduler.running else "stopped",
        database=db_ok,
    )


@app.get("/", tags=["system"])
def root():
    """API root — returns name, version, and docs URL."""
    return {
        "name": "Automation Toolkit",
        "version": "1.0.0",
        "docs": "/docs",
        "description": "Upload CSV/Excel → Clean → Report → Alert",
    }
