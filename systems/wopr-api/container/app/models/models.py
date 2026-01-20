from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    note: Optional[str] = None
    version: Optional[str] = None
    model_status: Optional[str] = None
    familyid: Optional[int] = None
    shortname: Optional[str] = None
    # ... whatever fields Directus has for models table

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    note: Optional[str] = None
    version: Optional[str] = None
    model_status: Optional[str] = None
    familyid: Optional[int] = None
    shortname: Optional[str] = None
    # All fields optional for PATCH

class ModelResponse(ModelBase):
    id: int
    date_created: Optional[datetime] = None
    date_updated: Optional[datetime] = None
    # Fields that come back from Directus