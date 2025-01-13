from typing import Type

from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.sqltypes import NullType

from models import Audio
from schemas import AudioCreate

def create_audio(db: Session, audio: AudioCreate) -> Audio:
    db_audio = Audio(
        name=audio.file_path + audio.filename,
        category="",
    )
    db.add(db_audio)
    db.commit()
    db.refresh(db_audio)
    return db_audio

def get_audio_list(db: Session, category: str) -> list[Type[Audio]]:
    audioDb = db.query(Audio)
    if category is not None:
        if category == "unsorted":
            audioDb = audioDb.filter(or_(
                Audio.category == None,
                Audio.category == category
            ))
        else:
            audioDb = audioDb.filter(Audio.category == category)
    else:
        audioDb = audioDb.filter(Audio.category == None)

    return audioDb.all()

def update_audio(db: Session, audio_name: str, audio: AudioCreate) -> Type[Audio] | None:
    db_audio = db.query(Audio).filter(Audio.name == audio_name).first()
    if db_audio:
        db_audio.category = audio.category
        db.commit()
        db.refresh(db_audio)
    return db_audio
