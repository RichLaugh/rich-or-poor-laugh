from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from database import Base, engine, SessionLocal
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from dotenv import load_dotenv
import tempfile
from audio_similarity import AudioSimilarity
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import logging
from routes import user, category, audio
from model.model import predict_class
from fastapi.responses import JSONResponse
import json
import numpy as np
import random

load_dotenv()

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

app.mount("/audio-file", StaticFiles(directory=os.getenv('PATH_TO_AUDIO_LIB')), name="audio")
app.include_router(user.router, tags=["[DataMapper] User"])
app.include_router(category.router, prefix="/categories", tags=["[DataMapper] Category"])
app.include_router(audio.router, prefix="/audio", tags=["[DataMapper] Audio"])

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.generic):
            return obj.item()
        return super(NumpyEncoder, self).default(obj)

@app.get("/", tags=["App"])
def root():
    a = " world"
    b = "hello" + a
    return {"hello world": b}

@app.post("/audio-similarity", tags=["App"])
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

    # audio_similarity = AudioSimilarity(original_path, compare_path, sample_rate, weights, True, 1)

    # similarity_score = audio_similarity.stent_weighted_audio_similarity(metrics='all')

    # normalized_similarity_score = (
    #         0.4 * similarity_score['rhythm_similarity'] +
    #         0.4 * similarity_score['energy_envelope_similarity'] +
    #         0.2 * similarity_score['perceptual_similarity']
    # )

    predicted = predict_class(tmp_file_path)
    rounded_data = {k: round(float(v), 2) for k, v in predicted.items()}
    print(rounded_data)
    if (max(rounded_data.values()) == rounded_data['rich']):
        if (rounded_data['rich'] > 0.75):
            swass = rounded_data['rich']
        else:
            swass = random.uniform(0.65, 0.75)
    else:
        if (max(rounded_data.values()) == rounded_data['poor']):
            swass = rounded_data['rich']
        else:
            swass = random.uniform(0.65, 0.75)

    return {
        "predicted": rounded_data,
        "similarity_score": {
            "swass": swass
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv('HOST'),
        port=8000,
        reload=True,
        log_level="info"
    )