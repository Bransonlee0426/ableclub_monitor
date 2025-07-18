from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database.session import Base

class Keyword(Base):
    """
    SQLAlchemy model for the 'keywords' table.
    Each user can have multiple keywords for notification filtering.
    """
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    keyword = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Composite unique constraint to prevent duplicate keywords for the same user
    __table_args__ = (
        UniqueConstraint('user_id', 'keyword', name='_user_keyword_uc'),
    )

    # Relationship to User model (commented out to avoid circular import)
    # user = relationship("User", back_populates="keywords") 