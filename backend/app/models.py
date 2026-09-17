from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .config import DATABASE_URL
from .database import Base

BoundaryGeometry = Geometry("GEOMETRY", srid=4326, spatial_index=True) if DATABASE_URL.startswith("postgresql") else Text()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped[User] = relationship()
    sites: Mapped[list["Site"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Site(Base):
    __tablename__ = "sites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    region: Mapped[str] = mapped_column(String(160))
    area_hectares: Mapped[float] = mapped_column(Float)
    boundary_geojson: Mapped[str | None] = mapped_column(Text, nullable=True)
    boundary_geometry: Mapped[str | None] = mapped_column(BoundaryGeometry, nullable=True)
    carbon_tco2e: Mapped[float] = mapped_column(Float, default=0)
    biodiversity_index: Mapped[float] = mapped_column(Float, default=0)
    project: Mapped[Project] = relationship(back_populates="sites")
