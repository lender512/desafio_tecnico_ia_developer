from typing import Generator


class MockDatabase:
    """
    Mockup database class
    """
    
    def __init__(self):
        """Initialize database"""
        pass
    
    def close(self):
        """Close database connection (mockup)"""
        pass


def get_db() -> Generator[MockDatabase, None, None]:
    """
    Get database instance for dependency injection
    Similar to SQLAlchemy session pattern
    """
    db = MockDatabase()
    try:
        yield db
    finally:
        db.close()
