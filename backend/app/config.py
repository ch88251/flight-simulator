from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://flightsim:flightsim@localhost:5432/flightsim"
    num_aircraft: int = 5


settings = Settings()
