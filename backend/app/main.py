import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api import aircraft, airports
from app.config import settings
from app.db import SessionLocal, get_db
from app.fleet import replace_fleet
from app.simulation_loop import run_simulation

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    with SessionLocal() as db:
        replace_fleet(db, settings.num_aircraft)

    # Note: the simulation runs inside the API process, so run a single worker.
    task = None
    if settings.simulation_enabled:
        task = asyncio.create_task(
            run_simulation(settings.sim_time_scale, settings.sim_tick_seconds)
        )
    yield
    if task is not None:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="Flight Simulator API", lifespan=lifespan)
app.include_router(airports.router)
app.include_router(aircraft.router)


@app.get("/api/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok", "database": "ok"}
