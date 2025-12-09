# app/db/init_db.py
from .session import engine
from .base import Base

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("DB initialized!")

if __name__ == "__main__":
    init_db()
