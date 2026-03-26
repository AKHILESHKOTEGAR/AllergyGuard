import google.generativeai as genai
from PIL import Image
import io
import os
import json
from sqlalchemy.orm import Session
from app.models import models
from dotenv import load_dotenv

load_dotenv()

def scan_and_analyze(image_bytes: bytes, user_profile: dict, db: Session):
    # 1. Force configuration inside the function
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # 2. Refined Prompt for JSON-only output
        prompt = "List all ingredients from this image. Output ONLY a JSON array of strings. No formatting, no markdown."
        response = model.generate_content([prompt, img])
        
        # Log the raw response for debugging in the uvicorn terminal
        print(f"RAW AI RESPONSE: {response.text}")
        
        # Clean the response string
        text_data = response.text.strip().replace("```json", "").replace("```", "")
        extracted_ingredients = json.loads(text_data)
        
        # 3. Analysis Logic
        found_problems = []
        # Ensure we have a list of allergens, even if empty
        user_allergens = [a.lower() for a in user_profile.get("primary_allergens", [])]
        
        for ing in extracted_ingredients:
            ing_lower = ing.lower()
            # Check DB for hidden matches
            db_match = db.query(models.Ingredient).filter(models.Ingredient.name == ing_lower).first()
            
            if db_match and db_match.allergen_category.lower() in user_allergens:
                found_problems.append({
                    "ingredient": ing, 
                    "reason": f"Hidden source of {db_match.allergen_category}"
                })
        
        status = "Danger" if found_problems else "Safe"
        return {
            "status": status,
            "extracted_ingredients": extracted_ingredients,
            "conflicts": found_problems
        }

    except Exception as e:
        print(f"DETAILED SCANNER ERROR: {str(e)}")
        raise e