# Darukaa.Earth

Darukaa.Earth is a full-stack platform for teams stewarding carbon and biodiversity projects. It gives administrators one place to create projects, add mapped sites, assess portfolio health, and review change over time.

## Highlights

- A responsive React portfolio dashboard with clear carbon, area, biodiversity, site-health, and activity views.
- A JWT-protected registration/login flow. Each new account receives its own project and illustrative demo portfolio; all subsequent site creation is persisted through the API.
- A focused site-creation flow and searchable/filterable portfolio table.
- A map experience designed for Mapbox GL JS; configure a public Mapbox token to activate the live satellite map and polygon drawing tools (`MapboxDraw`). The polished local fallback keeps the demo useful without exposing a token.
- A FastAPI REST API with JWT registration/login, ownership checks, projects, sites, GeoJSON boundary capture, and API-backed dashboard metrics.
- PostGIS-ready Docker Compose development environment, automated lint/test/build CI, Prettier/lint-staged Husky hooks, and backend Ruff checks.

## Architecture

```text
React + Vite (frontend) ──JWT──> FastAPI (backend) ──SQLAlchemy──> PostgreSQL + PostGIS
      Mapbox GL JS / Draw                 │
      Chart.js                            └── project and site API
```

The frontend is deliberately usable with fixture data so design review and UI work do not depend on an API or a Mapbox key. In production, `VITE_API_URL` points it at the FastAPI deployment and `VITE_MAPBOX_TOKEN` enables satellite basemaps and draw controls.

## Database schema

| Table | Purpose | Important fields |
| --- | --- | --- |
| `users` | Authenticated administrators | `id`, `email` (unique), `password_hash`, `created_at` |
| `projects` | A managed environmental programme | `id`, `owner_id` → users, `name`, `description` |
| `sites` | A monitored project area | `id`, `project_id` → projects, `name`, `region`, `area_hectares`, `boundary_geojson`, `boundary_geometry`, `carbon_tco2e`, `biodiversity_index` |

The Compose database is the PostGIS image. On PostgreSQL, startup enables the PostGIS extension and `boundary_geometry` is an SRID 4326 spatial column with a spatial index. `boundary_geojson` retains the original Mapbox-drawn payload for portable API responses and auditability. SQLite remains available for local quick-start development.

## Local setup

Prerequisites: Node 20+, Python 3.12+, and Docker (optional, for PostgreSQL/PostGIS).

```bash
# Frontend
cp frontend/.env.example frontend/.env
npm --prefix frontend install
npm --prefix frontend run dev

# Backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
# backend/.env is included for local development; copy .env.example for a fresh setup.
uvicorn app.main:app --app-dir backend --reload
```

The web UI runs at `http://localhost:5173`; API documentation is at `http://localhost:8000/docs`. For a PostGIS database and containerized API instead:

```bash
docker compose up --build
```

Use a strong `JWT_SECRET` and real `DATABASE_URL` outside development. Add a Mapbox public token to `frontend/.env` for the live map:

```env
VITE_MAPBOX_TOKEN=pk.your_public_mapbox_token
VITE_API_URL=http://localhost:8000
```

## API sketch

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Register and receive a JWT |
| `POST` | `/auth/login` | Authenticate and receive a JWT |
| `GET`, `POST` | `/projects` | List or create owned projects |
| `GET`, `POST` | `/projects/{id}/sites` | List or create sites for an owned project |

Protected endpoints expect `Authorization: Bearer <token>`. The React client stores this token locally after login and sends it with all project/site requests.

## Quality and CI/CD

Run quality checks locally:

```bash
npm --prefix frontend run lint
npm --prefix frontend run test
npm --prefix frontend run build
ruff check backend
pytest backend/tests
```

The GitHub Actions workflow runs these frontend and backend checks on every push and pull request. Husky runs `lint-staged` at commit time, formatting staged frontend source with Prettier and Python source with Ruff. `render.yaml` defines the Render API/database blueprint; connect the frontend folder to Vercel and set `VITE_API_URL` and `VITE_MAPBOX_TOKEN`. Set Render `FRONTEND_ORIGINS` to the Vercel URL. Both platforms can auto-deploy from the default branch after CI passes. See [SUBMISSION.md](SUBMISSION.md) for the final handoff checklist.

## Data choice

The dashboard uses intentional fixtures modeled after Indian restoration landscapes (mangrove, dry forest, wildlife corridor, community forest). They are illustrative rather than claims about real projects, which makes the application safe to demo while showing meaningful environmental metrics and trend interactions.
