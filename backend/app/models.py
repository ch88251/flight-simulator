from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

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
