from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ModelFamilyBase(BaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    # ... whatever fields Directus has for models table

class ModelFamilyCreate(ModelFamilyBase):
    pass

class ModelFamilyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    # All fields optional for PATCH

class ModelFamilyResponse(ModelFamilyBase):
    id: str
    date_created: Optional[datetime] = None
    date_updated: Optional[datetime] = None
    # Fields that come back from Directus