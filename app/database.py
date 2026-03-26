from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Get the URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Debugging print (This will show up in your uvicorn logs)
print(f"DEBUG: Connecting to database at: {SQLALCHEMY_DATABASE_URL}")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is missing! Check your .env file.")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()