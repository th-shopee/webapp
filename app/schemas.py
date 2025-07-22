from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ErrorCreate(BaseModel):
    basket_id: str
    error_type: str
    station_id: str
    comment: Optional[str] = None

class ErrorResponse(ErrorCreate):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True  # Enable ORM support
    }
