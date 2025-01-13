from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from crud.category import get_categories, create_category
from models import get_db, Audio, Category
from sqlalchemy import func
from schemas import CategoryCreate, CategoryRead

router = APIRouter()

@router.get("", response_model=list[CategoryRead])
async def read_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()  # Get all categories

    # Get the count of audios for each category
    result = []
    for category in categories:
        if category.name == 'unsorted':
            audio_count = db.query(func.count(Audio.id)).filter(or_(
        Audio.category == None,
        Audio.category == "unsorted"
    )).scalar()
        else:
            audio_count = db.query(func.count(Audio.id)).filter(Audio.category == category.name).scalar()
        category_dict = category.__dict__  # Convert SQLAlchemy model to dict
        category_dict["audio_count"] = audio_count
        result.append(category_dict)
    return result

@router.post("", response_model=CategoryRead)
async def create_new_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, data)
