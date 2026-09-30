# Flight Simulator

Simulates air traffic: aircraft fly between real airports, with Table and Map views.

**Stack:** FastAPI · SQLAlchemy · Alembic · PostgreSQL · React · Docker Compose

## Running locally

```bash
docker compose up --build
```

| Service  | URL                                   |
|----------|---------------------------------------|
| API      | http://localhost:8000/api/health      |
| API docs | http://localhost:8000/docs            |
| Postgres | localhost:5432 (flightsim/flightsim)  |

The backend source is bind-mounted, and uvicorn reloads when you change the code.

## Database migrations

Migrations run automatically (`alembic upgrade head`) when the backend container starts.
To create a new migration after changing the models:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe change"
```
