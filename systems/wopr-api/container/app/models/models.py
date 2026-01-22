from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ============================================================================
# Model Status/Version/Operations Nested Structures
# ============================================================================

class ModelStatusDict(BaseModel):
    """Runtime file status for wopr-model service"""
    backup: Optional[dict] = None
    checksum: Optional[str] = None
    has_distfile: Optional[bool] = None
    filename: Optional[str] = None
    active: bool


class ModelVersionDict(BaseModel):
    """Version tracking for models"""
    current_version: int
    note: Optional[str] = None
    wopr_version: Optional[str] = None
    previous_versions: Optional[dict] = None


class ModelOperationsDict(BaseModel):
    """Model operation tracking"""
    task: str
    data: str
    note: str
    extradata: str
    status: str


# ============================================================================
# Model Classes (ML Models in Directus)
# ============================================================================

class ModelBase(BaseModel):
    """Base model metadata - stored in Directus models table"""
    name: str
    familyid: int
    model_status: ModelStatusDict
    version: ModelVersionDict
    note: Optional[str] = None
    shortname: Optional[str] = None
    operations: Optional[ModelOperationsDict] = None
    description: Optional[str] = None
    date_updated: Optional[datetime] = None


class ModelCreate(ModelBase):
    """Create new model - inherits all ModelBase fields"""
    pass


class ModelUpdate(BaseModel):
    """Update existing model - all fields optional"""
    name: Optional[str] = None
    description: Optional[str] = None
    note: Optional[str] = None
    version: Optional[int] = None
    model_status: Optional[str] = None
    familyid: Optional[int] = None
    shortname: Optional[str] = None
    date_updated: Optional[datetime] = None
    url: Optional[str] = None


class ModelResponse(ModelBase):
    """Model response with database fields"""
    id: int
    date_created: Optional[datetime] = None
    date_updated: Optional[datetime] = None


# ============================================================================
# ModelFamily Classes (Model grouping in Directus)
# ============================================================================

class ModelFamilyBase(BaseModel):
    """Model family grouping - stored in Directus model_family table"""
    name: str
    description: Optional[str] = None
    note: Optional[str] = None
    version: Optional[str] = None
    url: Optional[str] = None


class ModelFamilyCreate(ModelFamilyBase):
    """Create new model family"""
    pass


class ModelFamilyUpdate(BaseModel):
    """Update model family - all fields optional"""
    name: Optional[str] = None
    description: Optional[str] = None
    note: Optional[str] = None
    version: Optional[str] = None
    url: Optional[str] = None


class ModelFamilyResponse(ModelFamilyBase):
    """Model family response with database fields"""
    id: int
    date_created: Optional[datetime] = None
    date_updated: Optional[datetime] = None


# ============================================================================
# Game Classes (Game catalog in Directus)
# ============================================================================

class GameCreate(BaseModel):
    """Create new game entry"""
    name: str
    description: Optional[str] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    url: Optional[str] = None
    status: str
    user_created: Optional[UUID] = None


class GameUpdate(BaseModel):
    """Update game - all fields optional"""
    name: Optional[str] = None
    description: Optional[str] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    url: Optional[str] = None
    status: Optional[str] = None
    user_updated: Optional[UUID] = None


class GameResponse(BaseModel):
    """Game response - stored in Directus games table"""
    id: int
    uuid: UUID
    name: str
    description: Optional[str] = None
    min_players: Optional[int] = None
    max_players: Optional[int] = None
    url: Optional[str] = None
    status: str
    user_created: Optional[UUID] = None
    date_created: datetime
    user_updated: Optional[UUID] = None
    date_updated: Optional[datetime] = None


# ============================================================================
# Player Classes (Player info in Directus)
# ============================================================================

class PlayerPayload(BaseModel):
    """Player information - stored in Directus players table"""
    name: str
    isbot: Optional[bool] = None


# ============================================================================
# Play Classes (Game plays/moves in Directus)
# ============================================================================

class PlayPayload(BaseModel):
    """Individual game plays/moves - stored in Directus playtracker table"""
    playerid: int
    gameid: int
    playid: int
    note: str
    filename: str