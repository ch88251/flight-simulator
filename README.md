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

## Backend development

The backend uses [uv](https://docs.astral.sh/uv/) for dependency management and
[Ruff](https://docs.astral.sh/ruff/) for linting and formatting (configured in
`backend/pyproject.toml`).

```bash
cd backend
uv sync                      # create .venv with app + dev dependencies (for your editor)
uv run ruff check .          # lint
uv run ruff check --fix .    # lint and apply safe fixes
uv run ruff format .         # format
uv add <package>             # add a runtime dependency (updates uv.lock)
uv add --dev <package>       # add a dev-only dependency
```

After changing dependencies, rebuild the image with `docker compose up --build`.
Inside the container the virtualenv lives at `/opt/venv`, so commands such as
`docker compose exec backend ruff check .` also work.
Migrations generated with `alembic revision --autogenerate` are automatically
linted and formatted with Ruff.
