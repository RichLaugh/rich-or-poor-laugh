from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from schemas import UserCreate, UserRead, Token, AudioCreate
from models import User, Audio
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from schemas import TokenData
import os
from dotenv import load_dotenv
import tempfile
from audio_similarity import AudioSimilarity
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import logging

load_dotenv()

# Создать все таблицы
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)

app = FastAPI()
origins = [
    "*",  # any
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # List of allowed origins
    allow_credentials=True,           # Whether to allow cookies/authentication
    allow_methods=["*"],              # List of allowed HTTP methods
    allow_headers=["*"],              # List of allowed HTTP headers
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.mount("/audio", StaticFiles(directory=os.getenv('PATH_TO_AUDIO_LIB')), name="audio")
@app.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},  # 'sub' - стандартное поле для subject
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/mark")
def mark(audio: AudioCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_audio = Audio(
        name=audio.name,
        category=audio.category,
        user_id=current_user.id
    )
    db.add(new_audio)
    db.commit()
    db.refresh(new_audio)
    return new_audio

@app.post("/audio-similarity")
async def audio_similarity(file: UploadFile = File(...)):
    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(contents)
        tmp_file_path = tmp_file.name

    original_path = './audio_folder/richlaugh.wav'  # Ensure this file exists
    compare_path = tmp_file_path

    sample_rate = 44100
    weights = {
        'zcr_similarity': 0.05,
        'rhythm_similarity': 0.35,
        'chroma_similarity': 0.05,
        'energy_envelope_similarity': 0.35,
        'spectral_contrast_similarity': 0.05,
        'perceptual_similarity': 0.25
    }

    audio_similarity = AudioSimilarity(original_path, compare_path, sample_rate, weights, True, 1)

    similarity_score = audio_similarity.stent_weighted_audio_similarity(metrics='all')

    normalized_similarity_score = (
            0.4 * similarity_score['rhythm_similarity'] +
            0.4 * similarity_score['energy_envelope_similarity'] +
            0.2 * similarity_score['perceptual_similarity']
    )

    return {
        "similarity_score": similarity_score,
        "normalized_similarity_score":normalized_similarity_score,
    }

@app.get("/audio-list")
async def audio_list(current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    user = current_user
    directory = os.getenv('PATH_TO_AUDIO_LIB')
    items = os.listdir(directory)
    files = [f for f in items if os.path.isfile(os.path.join(directory, f))]

    db_audio_names = db.query(Audio.name) \
        .filter(Audio.user_id == current_user.id) \
        .all()
    # Преобразуем список кортежей [(name1,), (name2,), ...] в список строк
    db_audio_names = [name_tuple[0] for name_tuple in db_audio_names]

    # Отфильтровать файлы, которые уже отмечены (есть в БД)
    unmarked_files = [f for f in files if f not in db_audio_names]

    results = []
    for idx, filename in enumerate(unmarked_files, start=1):
        results.append({
            "id": str(idx),
            "name": filename,
            "path": f"http://localhost:8000/audio/{filename}",
            "duration": 0
        })

    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,  # Enable reload if desired
        log_level="info"
    )