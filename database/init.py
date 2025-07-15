"""
Database initialization module
Handles automatic table creation and database setup
"""

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from core.config import settings
from database.session import engine
import logging

# Import all models to ensure they are registered with SQLAlchemy
from models.user import User
from models.event import Event  
from models.invitation_code import InvitationCode
from models.notify_setting import NotifySetting

# Get all model metadata
from models.user import Base as UserBase
from models.event import Base as EventBase
from models.invitation_code import Base as InvitationBase
from models.notify_setting import Base as NotifyBase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_tables_exist() -> dict:
    """
    Check which tables exist in the database
    
    Returns:
        dict: Dictionary with table names as keys and existence status as values
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        required_tables = ['users', 'events', 'invitation_codes', 'notify_settings']
        table_status = {}
        
        for table in required_tables:
            table_status[table] = table in existing_tables
            
        return table_status
    except SQLAlchemyError as e:
        logger.error(f"Error checking tables: {e}")
        return {}

def create_tables():
    """
    Create all database tables if they don't exist
    This function is safe to run multiple times - it won't overwrite existing tables
    """
    try:
        logger.info("Starting database table creation...")
        
        # Check current table status
        table_status = check_tables_exist()
        logger.info(f"Current table status: {table_status}")
        
        # Create all tables from all models
        # Using create_all with checkfirst=True (default) ensures existing tables are not affected
        UserBase.metadata.create_all(bind=engine, checkfirst=True)
        EventBase.metadata.create_all(bind=engine, checkfirst=True)  
        InvitationBase.metadata.create_all(bind=engine, checkfirst=True)
        NotifyBase.metadata.create_all(bind=engine, checkfirst=True)
        
        logger.info("Database tables creation completed successfully")
        
        # Check final status
        final_status = check_tables_exist()
        logger.info(f"Final table status: {final_status}")
        
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during table creation: {e}")
        return False

def init_database():
    """
    Initialize the database with all required tables and basic data
    """
    logger.info(f"Initializing database: {settings.DATABASE_URL}")
    
    # Create tables
    if create_tables():
        logger.info("Database initialization completed successfully")
        return True
    else:
        logger.error("Database initialization failed")
        return False

def get_database_info():
    """
    Get information about the current database state
    
    Returns:
        dict: Database information including URL, tables, etc.
    """
    try:
        table_status = check_tables_exist()
        
        return {
            "database_url": settings.DATABASE_URL,
            "database_type": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql",
            "tables": table_status,
            "all_tables_exist": all(table_status.values()) if table_status else False
        }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Allow running this script directly to initialize the database
    init_database()