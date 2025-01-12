import click
import os
from database import SessionLocal
from models import Audio

@click.command()
def scan_audio():
    db = SessionLocal()
    directory = os.getenv('PATH_TO_AUDIO_LIB', '/app/audio')
    print(f"Scanning audio files... {directory}")
    items = os.listdir(directory)
    existing_files = set([audio.name for audio in db.query(Audio.name).all()])
    files = [f for f in items if os.path.isfile(os.path.join(directory, f))]
    new_files = [f for f in files if f not in existing_files]

    for f in new_files:
        print(f"Inserting {f} into the database")
        new_audio = Audio(name=f)
        db.add(new_audio)

    if new_files:
        db.commit()

