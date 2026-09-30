from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Airport
from app.schemas import AirportOut

router = APIRouter(prefix="/api/airports", tags=["airports"])


@router.get("", response_model=list[AirportOut])
def list_airports(db: Session = Depends(get_db)) -> list[Airport]:
    return list(db.scalars(select(Airport).order_by(Airport.code)))


@router.get("/{code}", response_model=AirportOut)
def get_airport(code: str, db: Session = Depends(get_db)) -> Airport:
    airport = db.scalar(select(Airport).where(Airport.code == code.upper()))
    if airport is None:
        raise HTTPException(status_code=404, detail=f"airport {code!r} not found")
    return airport
