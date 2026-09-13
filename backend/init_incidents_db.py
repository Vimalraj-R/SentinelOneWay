"""
Initialize incident tables in database.

Run this to create the incidents table schema.
"""
from database.base import Base, engine
from database.incident_models import Incident

def init_incident_tables():
    """Create incident tables."""
    print("Creating incident tables...")
    Base.metadata.create_all(bind=engine, tables=[Incident.__table__])
    print("Incident tables created successfully!")

if __name__ == '__main__':
    init_incident_tables()
