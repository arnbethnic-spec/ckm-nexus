"""Website model for WordPress site management."""
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base


class Website(Base):
    """Website model for storing WordPress site credentials."""
    
    __tablename__ = "websites"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = Column(String(200), nullable=False)
    base_url = Column(String(500), nullable=False)
    username = Column(String(200), nullable=False)
    encrypted_password = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
