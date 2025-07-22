from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from .database import Base

class Error(Base):
    __tablename__ =  "error"
    id = Column(Integer, primary_key=True, index=True)
    basket_id = Column(String(50))
    error_type = Column(String(100))
    station_id = Column(String(50))
    comment = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    