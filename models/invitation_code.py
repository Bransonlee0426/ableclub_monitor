from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class InvitationCode(Base):
    """
    SQLAlchemy model for the 'invitation_codes' table.
    """
    __tablename__ = "invitation_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
