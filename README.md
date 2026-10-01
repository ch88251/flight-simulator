# Flight Simulator

Simulates air traffic: aircraft fly between real airports, with Table and Map views.

**Stack:** FastAPI · SQLAlchemy · Alembic · PostgreSQL · React · Docker Compose

## Running locally

```bash
docker compose up --build
```

| Service  | URL                                   |
|----------|---------------------------------------|
| Web app  | http://localhost:5173                 |
| API      | http://localhost:8000/api/health      |
| API docs | http://localhost:8000/docs            |
| Postgres | localhost:5432 (flightsim/flightsim)  |

The backend and frontend sources are bind-mounted, so uvicorn and Vite reload when
you change the code. If port 5173 is taken, choose another host port with
`FRONTEND_PORT=5174 docker compose up` (or put `FRONTEND_PORT=5174` in a `.env` file).

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

## Frontend development

The frontend is React + TypeScript, built with [Vite](https://vite.dev/). In development
the Vite server forwards `/api` requests to the backend.

```bash
cd frontend
npm install        # install dependencies locally (for your editor)
npm run lint       # ESLint
npm run build      # type-check and build for production
```

The container keeps its own `node_modules` in an anonymous volume. After adding or
upgrading npm packages, rebuild it and renew that volume:

```bash
docker compose up --build -V frontend
```

The Map view uses [Leaflet](https://leafletjs.com/) with OpenStreetMap tiles, so it
needs internet access to load the map background.
