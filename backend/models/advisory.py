from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Advisory(Document):
    user_id: Optional[PydanticObjectId] = None
    farm_id: Optional[PydanticObjectId] = None
    query: str
    response: str
    recommended_crop: Optional[str] = None
    confidence: Optional[float] = None
    shap_factors: List[Dict[str, Any]] = []
    treatment_plan: Optional[List[str]] = []
    fertilizer_plan: Optional[List[Dict[str, Any]]] = []
    weather_advisory: Optional[str] = None
    language: str = "en"
    sources: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "advisories"


class ChatMessage(Document):
    """Stores individual chat conversations from the Voice Advisory Chat."""
    user_id: Optional[PydanticObjectId] = None
    query: str
    answer: str
    location: str = "Hyderabad"
    detected_location: Optional[str] = None
    language: str = "en"
    sources: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chat_messages"
