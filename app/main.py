from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models import models
from app.utils.ai_handler import get_structured_profile
from pydantic import BaseModel
from fastapi import UploadFile, File
from app.utils.scanner import scan_and_analyze

# This is the line the error is looking for!
app = FastAPI(title="AllergyGuard API")

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Pydantic Schema for the request body
class ProfileCreate(BaseModel):
    name: str
    raw_bio: str

@app.get("/")
def health_check():
    return {"status": "AllergyGuard API is live"}

@app.post("/onboarding/{user_id}")
def create_ai_profile(user_id: int, profile_data: ProfileCreate, db: Session = Depends(get_db)):
    try:
        # Call the Gemini AI logic
        structured_data = get_structured_profile(profile_data.raw_bio)
        
        # Save to Postgres
        new_profile = models.Profile(
            name=profile_data.name,
            user_id=user_id,
            allergy_requirements=structured_data
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        
        return {
            "message": "Profile created successfully",
            "structured_allergens": structured_data
        }
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan/{profile_id}")
async def upload_label(profile_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Read the bytes properly
    try:
        image_data = await file.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="Empty image file")
            
        results = scan_and_analyze(image_data, profile.allergy_requirements, db)
        return results
    except Exception as e:
        print(f"Scanner Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))