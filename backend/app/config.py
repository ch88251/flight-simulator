from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://flightsim:flightsim@localhost:5432/flightsim"


settings = Settings()
