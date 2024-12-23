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

@app.post("/test")
async def upload_audio(file: UploadFile = File(...)):
    # Прочитаем содержимое файла
    contents = await file.read()

    # Допустим, вы хотите выполнить некоторую логику обработки аудио.
    # Здесь мы просто вернём информацию о размере файла.
    file_info = {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size_bytes": len(contents)
    }

    return JSONResponse(content=file_info)


@app.post("/audio-similarity")
async def audio_similarity(file: UploadFile = File(...)):
    # Paths to the original and compariosn audio files/folders
    contents = await file.read()
    file_info = {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size_bytes": len(contents)
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(contents)
        tmp_file_path = tmp_file.name
    # return JSONResponse(content=file_info)

    original_path = './audio_folder/5.wav'  # Ensure this file exists
    compare_path = tmp_file_path

    # Set the sample rate and weights for the metrics

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


def plot_spectrogram(file, title):
    y, sr = librosa.load(file, sr=16000)
    S = librosa.feature.melspectrogram(y=y, sr=sr)
    S_db = librosa.power_to_db(S, ref=np.max)

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='mel')
    plt.colorbar(format='%+2.0f dB')
    plt.title(title)
    plt.tight_layout()


# plot_spectrogram("1.wav", "Laugh 1")
# plot_spectrogram("3.wav", "Laugh 2")

# audio_similarity()
# plt.show()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,  # Enable reload if desired
        log_level="info"
    )