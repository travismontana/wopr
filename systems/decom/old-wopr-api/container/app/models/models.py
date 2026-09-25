from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

# ============================================================================
# Model Status/Version/Operations Nested Structures
# ============================================================================


class ModelStatusDict(BaseModel):
    """Runtime file status for wopr-model service"""

    backup: dict | None = None
    checksum: str | None = None
    has_distfile: bool | None = None
    filename: str | None = None
    active: bool


class ModelVersionDict(BaseModel):
    """Version tracking for models"""

    current_version: int
    note: str | None = None
    wopr_version: str | None = None
    previous_versions: dict | None = None


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
    model_status: ModelStatusDict | None = None
    version: ModelVersionDict | None = None
    note: str | None = None
    shortname: str | None = None
    operations: ModelOperationsDict | None = None
    description: str | None = None
    date_updated: datetime | None = None


class ModelCreate(ModelBase):
    """Create new model - inherits all ModelBase fields"""


class ModelUpdate(BaseModel):
    """Update existing model - all fields optional"""

    name: str | None = None
    familyid: int | None = None
    model_status: ModelStatusDict | None = None
    version: ModelVersionDict | None = None
    note: str | None = None
    shortname: str | None = None
    operations: ModelOperationsDict | None = None
    description: str | None = None
    date_updated: datetime | None = None


class ModelResponse(ModelBase):
    """Model response with database fields"""

    id: int
    date_created: datetime | None = None
    date_updated: datetime | None = None


# ============================================================================
# ModelFamily Classes (Model grouping in Directus)
# ============================================================================


class ModelFamilyBase(BaseModel):
    """Model family grouping - stored in Directus model_family table"""

    name: str
    description: str | None = None
    note: str | None = None
    version: str | None = None
    url: str | None = None


class ModelFamilyCreate(ModelFamilyBase):
    """Create new model family"""


class ModelFamilyUpdate(BaseModel):
    """Update model family - all fields optional"""

    name: str | None = None
    description: str | None = None
    note: str | None = None
    version: str | None = None
    url: str | None = None


class ModelFamilyResponse(ModelFamilyBase):
    """Model family response with database fields"""

    id: int
    date_created: datetime | None = None
    date_updated: datetime | None = None


# ============================================================================
# Game Classes (Game catalog in Directus)
# ============================================================================


class GameCreate(BaseModel):
    """Create new game entry"""

    name: str
    description: str | None = None
    min_players: int | None = None
    max_players: int | None = None
    url: str | None = None
    status: str
    user_created: UUID | None = None


class GameUpdate(BaseModel):
    """Update game - all fields optional"""

    name: str | None = None
    description: str | None = None
    min_players: int | None = None
    max_players: int | None = None
    url: str | None = None
    status: str | None = None
    user_updated: UUID | None = None


class GameResponse(BaseModel):
    """Game response - stored in Directus games table"""

    id: int
    uuid: UUID
    name: str
    description: str | None = None
    min_players: int | None = None
    max_players: int | None = None
    url: str | None = None
    status: str
    user_created: UUID | None = None
    date_created: datetime
    user_updated: UUID | None = None
    date_updated: datetime | None = None


# ============================================================================
# Player Classes (Player info in Directus)
# ============================================================================


class PlayerPayload(BaseModel):
    """Player information - stored in Directus players table"""

    name: str
    isbot: bool | None = None


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
