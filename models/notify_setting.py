from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.user import Base


class NotifySetting(Base):
    """
    SQLAlchemy model for the 'notify_settings' table.
    
    This model manages user notification preferences including email notifications.
    Each user can have multiple notification settings for different notification types.
    """
    __tablename__ = "notify_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    notify_type = Column(String(50), nullable=False)
    email_address = Column(String(255), nullable=True)  # Optional, but required when notify_type is 'email'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to User model
    user = relationship("User", back_populates="notify_settings")