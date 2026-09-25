from datetime import datetime

from pydantic import BaseModel


class ModelFamilyBase(BaseModel):
    name: str
    description: str | None = None
    note: str | None = None
    version: str | None = None
    url: str | None = None
    # ... whatever fields Directus has for models table


class ModelFamilyCreate(ModelFamilyBase):
    pass


class ModelFamilyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    note: str | None = None
    version: str | None = None
    url: str | None = None
    # All fields optional for PATCH


class ModelFamilyResponse(ModelFamilyBase):
    id: int
    date_created: datetime | None = None
    date_updated: datetime | None = None
    # Fields that come back from Directus
