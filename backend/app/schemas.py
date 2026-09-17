from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(UserCreate):
    pass


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=1000)


class ProjectRead(ProjectCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SiteCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    region: str = Field(min_length=2, max_length=160)
    area_hectares: float = Field(gt=0)
    boundary_geojson: dict | None = None
    carbon_tco2e: float = Field(default=0, ge=0)
    biodiversity_index: float = Field(default=0, ge=0, le=100)


class SiteRead(SiteCreate):
    id: int
    project_id: int
    model_config = ConfigDict(from_attributes=True)
