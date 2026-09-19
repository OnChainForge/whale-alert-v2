import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.logging_config import setup_logging
from app.listener import run_listener_loop
from app.dedup import dedup_health_check
from app import models, schemas

setup_logging()
logger = logging.getLogger("main")

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Starts the background listener when the app boots, cancels it on shutdown."""
    listener_task = asyncio.create_task(run_listener_loop())
    logger.info("Listener task started in background.")
    yield
    listener_task.cancel()
    logger.info("Listener task cancelled.")


app = FastAPI(
    title="Whale Alert",
    description="Detects large Ethereum transactions in real time, using Redis to deduplicate alerts.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "redis": dedup_health_check()}


@app.get("/alerts/", response_model=list[schemas.WhaleAlertOut])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(models.WhaleAlert).order_by(models.WhaleAlert.id.desc()).limit(50).all()
