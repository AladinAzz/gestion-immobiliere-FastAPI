# database.py

from sqlalchemy.orm import Session
from models import SessionLocal

# Dependency to get the DB session
def get_db():
    db = SessionLocal()  # Create a new session instance
    try:
        yield db  # Return the session to the route function
    finally:
        db.close()  # Close the session after the request is done
