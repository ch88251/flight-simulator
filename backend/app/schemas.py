from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import AircraftStatus


class AirportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    city: str
    latitude: float
    longitude: float
    altitude_ft: int


class AirportRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class AircraftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    callsign: str
    aircraft_type: str
    status: AircraftStatus
    latitude: float
    longitude: float
    altitude_ft: float
    heading_deg: float
    ground_speed_kts: float
    origin: AirportRef
    destination: AirportRef | None
    updated_at: datetime
