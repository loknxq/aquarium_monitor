from pydantic import BaseModel
from datetime import date
from typing import Dict, Optional

class MeasurementCreate(BaseModel):
    date: date
    values: Dict[str, float]

class MeasurementResponse(BaseModel):
    id: int
    parameter_id: int
    parameter_name: str
    date: date
    value: float

    class Config:
        from_attributes = True