import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import get_db, init_db
from app.routers import jobs, tasks
from app.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    logger.info("Database initialized")
    db = next(get_db())
    start_scheduler(db)
    yield
    # Shutdown
    stop_scheduler()
    logger.info("Scheduler stopped")


app = FastAPI(
    title="Automation Toolkit",
    description="Automate CSV/Excel processing with multi-channel alerts and scheduling.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(tasks.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "name": "Automation Toolkit",
        "version": "1.0.0",
        "docs": "/docs",
    }
