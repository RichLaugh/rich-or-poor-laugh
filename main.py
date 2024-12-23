import librosa
import os
import tempfile
import matplotlib.pyplot as plt
import numpy as np
from typing import Union
from audio_similarity import AudioSimilarity
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()

# @app.post("/test")
# async def upload_audio(file: UploadFile = File(...)):
#     contents = await file.read()
#
#     file_info = {
#         "filename": file.filename,
#         "content_type": file.content_type,
#         "file_size_bytes": len(contents)
#     }
#
#     return JSONResponse(content=file_info)


@app.post("/audio-similarity")
async def audio_similarity(file: UploadFile = File(...)):
    contents = await file.read()
    file_info = {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size_bytes": len(contents)
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(contents)
        tmp_file_path = tmp_file.name

    original_path = './audio_folder/richlaugh.wav'  # Ensure this file exists
    compare_path = tmp_file_path

    sample_rate = 44100
    weights = {
        'zcr_similarity': 0.2,
        'rhythm_similarity': 0.2,
        'chroma_similarity': 0.2,
        'energy_envelope_similarity': 0.1,
        'spectral_contrast_similarity': 0.1,
        'perceptual_similarity': 0.2
    }

    audio_similarity = AudioSimilarity(original_path, compare_path, sample_rate, weights, True, 1)

    similarity_score = audio_similarity.stent_weighted_audio_similarity(metrics='all')

    response = {
        "similarity_score": similarity_score,
    }

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,  # Enable reload if desired
        log_level="info"
    )