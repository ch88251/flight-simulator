from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Aircraft
from app.schemas import AircraftOut

router = APIRouter(prefix="/api/aircraft", tags=["aircraft"])

_with_airports = (joinedload(Aircraft.origin), joinedload(Aircraft.destination))


@router.get("", response_model=list[AircraftOut])
def list_aircraft(db: Session = Depends(get_db)) -> list[Aircraft]:
    return list(db.scalars(select(Aircraft).options(*_with_airports).order_by(Aircraft.callsign)))


@router.get("/{aircraft_id}", response_model=AircraftOut)
def get_aircraft(aircraft_id: int, db: Session = Depends(get_db)) -> Aircraft:
    aircraft = db.scalar(
        select(Aircraft).options(*_with_airports).where(Aircraft.id == aircraft_id)
    )
    if aircraft is None:
        raise HTTPException(status_code=404, detail=f"aircraft {aircraft_id} not found")
    return aircraft
