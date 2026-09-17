import json

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from .auth import create_access_token, get_current_user, hash_password, verify_password
from .config import FRONTEND_ORIGINS
from .database import Base, engine, get_db
from .models import Project, Site, User
from .schemas import (
    LoginRequest,
    ProjectCreate,
    ProjectRead,
    SiteCreate,
    SiteRead,
    Token,
    UserCreate,
)

if engine.dialect.name == "postgresql":
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Darukaa.Earth API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[
    FRONTEND_ORIGINS,
    "https://darukaa-eight.vercel.app",
    ], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],      # Allows all origins
#     allow_credentials=False,  # Must be False if allow_origins=["*"]
#     allow_methods=["*"],      # Allows all methods (GET, POST, etc.)
#     allow_headers=["*"],      # Allows all headers
# )


def serialize_site(site: Site) -> dict:
    return {
        "id": site.id,
        "project_id": site.project_id,
        "name": site.name,
        "region": site.region,
        "area_hectares": site.area_hectares,
        "boundary_geojson": json.loads(site.boundary_geojson) if site.boundary_geojson else None,
        "carbon_tco2e": site.carbon_tco2e,
        "biodiversity_index": site.biodiversity_index,
    }


def geojson_to_wkt(geometry: dict) -> str:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geometry_type not in {"Polygon", "MultiPolygon"} or not coordinates:
        raise HTTPException(status_code=422, detail="Boundary must be a GeoJSON Polygon or MultiPolygon")

    def ring_to_wkt(ring: list[list[float]]) -> str:
        return ", ".join(f"{point[0]} {point[1]}" for point in ring)

    if geometry_type == "Polygon":
        rings = ", ".join(f"({ring_to_wkt(ring)})" for ring in coordinates)
        return f"SRID=4326;POLYGON({rings})"
    polygons = ", ".join(
        f"({', '.join(f'({ring_to_wkt(ring)})' for ring in polygon)})" for polygon in coordinates
    )
    return f"SRID=4326;MULTIPOLYGON({polygons})"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return Token(access_token=create_access_token(user.id))


@app.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user.id))


@app.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = Project(**payload.model_dump(), owner_id=user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/projects", response_model=list[ProjectRead])
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.owner_id == user.id).order_by(Project.id.desc()).all()


@app.post("/projects/{project_id}/sites", response_model=SiteRead, status_code=status.HTTP_201_CREATED)
def create_site(project_id: int, payload: SiteCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    values = payload.model_dump()
    if values["boundary_geojson"] is not None:
        values["boundary_geometry"] = geojson_to_wkt(values["boundary_geojson"])
        values["boundary_geojson"] = json.dumps(values["boundary_geojson"])
    site = Site(**values, project_id=project_id)
    db.add(site)
    db.commit()
    db.refresh(site)
    return serialize_site(site)


@app.get("/projects/{project_id}/sites", response_model=list[SiteRead])
def list_sites(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return [serialize_site(site) for site in project.sites]
