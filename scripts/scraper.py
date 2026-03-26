import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import models

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

def seed_ingredients():
    db = SessionLocal()
    
    # Pre-defined mapping of common hidden names
    # In a real-world scenario, we'd scrape a larger table, 
    # but for reliability, we'll start with this high-accuracy core set.
    knowledge_base = {
        "Dairy": ["Casein", "Whey", "Lactose", "Ghee", "Curds", "Butterfat", "Recaldent"],
        "Egg": ["Albumin", "Globulin", "Lecithin", "Lysozyme", "Vitellin", "Ovalbumin"],
        "Wheat": ["Semolina", "Durum", "Einkorn", "Farina", "Spelt", "Bulgur", "Triticale"],
        "Peanut": ["Arachis oil", "Beer nuts", "Goober peas", "Ground nuts", "Mandelonas"],
        "Soy": ["Edamame", "Miso", "Natto", "Shoyu", "Tamari", "Tempeh", "Tofu"]
    }

    try:
        for allergen, derivatives in knowledge_base.items():
            for name in derivatives:
                # Check if exists to avoid duplicates
                exists = db.query(models.Ingredient).filter_by(name=name).first()
                if not exists:
                    new_ing = models.Ingredient(
                        name=name.lower(), 
                        allergen_category=allergen.lower(),
                        is_derivative=1
                    )
                    db.add(new_ing)
        
        db.commit()
        print("Successfully seeded 30+ core hidden allergens!")
    except Exception as e:
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_ingredients()