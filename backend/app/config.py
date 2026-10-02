from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://flightsim:flightsim@localhost:5432/flightsim"
    num_aircraft: int = 5

    simulation_enabled: bool = True
    # Simulated seconds that pass per real second (30 => a 5 h flight takes 10 min).
    sim_time_scale: float = 30.0
    # Real seconds between simulation ticks.
    sim_tick_seconds: float = 1.0


settings = Settings()
