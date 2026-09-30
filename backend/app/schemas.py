from pydantic import BaseModel, ConfigDict


class AirportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    city: str
    latitude: float
    longitude: float
    altitude_ft: int
