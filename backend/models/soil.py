from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional
from datetime import datetime

class SoilReading(Document):
    farm_id: Optional[PydanticObjectId] = None
    user_id: Optional[PydanticObjectId] = None
    N: float = Field(..., ge=0, le=140, description="Nitrogen ratio")
    P: float = Field(..., ge=0, le=145, description="Phosphorous ratio")
    K: float = Field(..., ge=0, le=205, description="Potassium ratio")
    temperature: float = Field(..., ge=0, le=50)
    humidity: float = Field(..., ge=0, le=100)
    ph: float = Field(..., ge=0, le=14)
    rainfall: float = Field(..., ge=0, le=300)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "soil_readings"
