"""Database service module for managing database connections and initialization."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database import Base, Status


class DatabaseService:
    def __init__(self, db_path='files/repair.db'):
        self.db_path = db_path
        self.engine = None
        self.Session = None

    def initialize(self):
        """Initialize database connection and create tables if needed"""
        # Ensure the files directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Check if database exists
        db_exists = os.path.exists(self.db_path)
        
        # Create engine
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        
        # Create session factory
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
        # Create tables if database is new
        if not db_exists:
            self._create_tables()
            self._populate_initial_data()

    def _create_tables(self):
        """Create all tables defined in the database models"""
        Base.metadata.create_all(self.engine)
        print("Database tables created successfully")

    def _populate_initial_data(self):
        """Populate initial required data"""
        session = self.Session()
        try:
            # Add default status
            default_status = Status(status='Backlog')
            session.add(default_status)
            session.commit()
            print("Initial data populated: Default status 'Backlog' created")
        except Exception as e:
            session.rollback()
            print(f"Error populating initial data: {e}")
            raise
        finally:
            session.close()

    def get_session(self):
        """Get a new database session"""
        if self.Session is None:
            raise RuntimeError("Database not initialized. Call initialize() first")
        return self.Session()

    def close(self):
        """Close database connections"""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()


# Global instance
db_service = DatabaseService()


# Convenience function for getting sessions
def get_db_session():
    """Get a database session from the global database service."""
    return db_service.get_session()