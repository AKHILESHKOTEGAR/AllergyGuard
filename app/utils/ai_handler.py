import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment!")
else:
    genai.configure(api_key=api_key)

def get_structured_profile(user_input: str):
    """
    Uses Gemini 2.0 Flash to convert free-text allergy descriptions 
    into a structured JSON profile.
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    You are an expert clinical allergist and nutritionist. 
    Transform this user's natural language input into a structured JSON profile for an allergy safety app.
    
    User Input: "{user_input}"
    
    Return ONLY a raw JSON object with this exact structure:
    {{
        "primary_allergens": ["list of major categories like dairy, peanuts, shellfish, etc."],
        "dietary_restrictions": ["vegan", "vegetarian", "halal", etc.],
        "specific_ingredients_to_avoid": ["specific chemicals, additives, or unique items mentioned"],
        "severity_notes": "any mentions of anaphylaxis or mild sensitivity"
    }}
    Do not include any markdown formatting or backticks, just the JSON string.
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean up the response text in case Gemini adds markdown backticks
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "").replace("```", "").strip()
        elif text_response.startswith("```"):
            text_response = text_response.replace("```", "").strip()
            
        return json.loads(text_response)
    except Exception as e:
        print(f"AI Processing Error: {e}")
        # Return a fallback structure if AI fails
        return {
            "primary_allergens": [],
            "dietary_restrictions": [],
            "specific_ingredients_to_avoid": [],
            "severity_notes": "Error processing input"
        }