from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Create the SQLAlchemy engine
# Configure connection arguments based on database type
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration for multi-threaded access
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL and other databases don't need special connect_args
    connect_args = {}

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a DB session
def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy database session.
    It ensures that the database session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()