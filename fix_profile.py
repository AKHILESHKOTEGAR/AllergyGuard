import requests
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

def reset_and_seed():
    with engine.connect() as conn:
        # 1. Clear existing data to start fresh
        conn.execute(text("TRUNCATE users, profiles RESTART IDENTITY CASCADE;"))
        
        # 2. Insert the User (ID 1)
        conn.execute(text(
            "INSERT INTO users (id, email, hashed_password) VALUES (1, 'akki@example.com', 'fake_hash');"
        ))
        
        # 3. Insert the Profile (linked to User 1)
        # Note: We are manually seeding the 'Dairy' allergy for testing
        allergy_json = '{"primary_allergens": ["dairy"], "dietary_restrictions": ["vegan"], "specific_ingredients_to_avoid": ["msg"]}'
        conn.execute(text(
            f"INSERT INTO profiles (id, name, user_id, allergy_requirements) VALUES (1, 'Akki', 1, '{allergy_json}');"
        ))
        conn.commit()
        print("Database Seeded: User #1 and Profile #1 (Dairy Allergy) are ready!")

if __name__ == "__main__":
    reset_and_seed()