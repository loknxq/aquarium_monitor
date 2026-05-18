from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class AquariumCreate(BaseModel):
    name: str
    inhabitants: Optional[str] = None
    parameters: List[int]
    photo: Optional[str] = None

class AquariumResponse(BaseModel):
    id: int
    name: str
    created_at: date
    inhabitants: Optional[str] = None
    photo: Optional[str] = None

    class Config:
        from_attributes = True
class ParameterResponse(BaseModel):
    id: int
    name: str
    display_name: str
    unit: str

    class Config:
        from_attributes = True