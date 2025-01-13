import os
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from crud.audio import get_audio_list
from models import User, Audio, get_db
from routes.user import get_current_user
from schemas import AudioCreate

router = APIRouter()


@router.get("/audio-list")
async def audio_list(db: Session = Depends(get_db),
                     category: str = Query(None, description="Filter audio by category")
                     ):
    audio_host = os.getenv('AUDIO_HOST')
    audio_records = get_audio_list(db, category)

    results = []
    for audio in audio_records:
        results.append({
            "id": audio.id,
            "name": audio.name,
            "url": audio_host + audio.name,
            "category": audio.category,
        })

    return results

@router.post("/mark")
def mark(audio: AudioCreate, db: Session = Depends(get_db)):
    new_audio = Audio(
        name=audio.name,
        category=audio.category,
    )
    db.add(new_audio)
    db.commit()
    db.refresh(new_audio)
    return new_audio
