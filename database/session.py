from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Create the SQLAlchemy engine
# The connect_args are specific to SQLite to allow multi-threaded access.
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
