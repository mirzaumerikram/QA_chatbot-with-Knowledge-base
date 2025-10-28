from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .db import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
