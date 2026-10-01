import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Airport(Base):
    __tablename__ = "airports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, index=True)  # IATA code
    name: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(80))
    latitude: Mapped[float] = mapped_column(Float)  # decimal degrees, + north
    longitude: Mapped[float] = mapped_column(Float)  # decimal degrees, + east
    altitude_ft: Mapped[int] = mapped_column(Integer)  # field elevation, feet MSL


class AircraftStatus(enum.StrEnum):
    ON_GROUND = "on_ground"
    CLIMBING = "climbing"
    CRUISING = "cruising"
    DESCENDING = "descending"
    LANDED = "landed"


class Aircraft(Base):
    __tablename__ = "aircraft"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    callsign: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    aircraft_type: Mapped[str] = mapped_column(String(40))
    status: Mapped[AircraftStatus] = mapped_column(
        Enum(
            AircraftStatus,
            name="aircraft_status",
            native_enum=False,
            length=20,
            values_callable=lambda e: [m.value for m in e],
        )
    )
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    altitude_ft: Mapped[float] = mapped_column(Float)  # feet MSL
    heading_deg: Mapped[float] = mapped_column(Float)  # 0-360, true north
    ground_speed_kts: Mapped[float] = mapped_column(Float)
    # On the ground, origin is the airport the aircraft is parked at.
    origin_airport_id: Mapped[int] = mapped_column(ForeignKey("airports.id"))
    destination_airport_id: Mapped[int | None] = mapped_column(ForeignKey("airports.id"))

    # Flight plan and progress (see app/simulation.py).
    cruise_speed_kts: Mapped[float] = mapped_column(Float, server_default="450")
    cruise_altitude_ft: Mapped[float] = mapped_column(Float, server_default="0")
    route_distance_nm: Mapped[float] = mapped_column(Float, server_default="0")
    distance_flown_nm: Mapped[float] = mapped_column(Float, server_default="0")
    # Simulated seconds left on the ground before departure (on_ground) or taxi-in (landed).
    ground_time_remaining_s: Mapped[float] = mapped_column(Float, server_default="0")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    origin: Mapped[Airport] = relationship(foreign_keys=[origin_airport_id])
    destination: Mapped[Airport | None] = relationship(foreign_keys=[destination_airport_id])
