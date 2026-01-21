from pydantic import BaseModel

class ModelStatus(BaseModel):
    model: str
    backedup: bool = False
    checksum: str = None
    has_distfile: bool = False
    filename: str = None