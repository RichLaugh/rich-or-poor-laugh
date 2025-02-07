import os
import sys
import random
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import butter, lfilter

# -----------------------
# Аугментации для аудио
# -----------------------

def augment_gaussian_noise(audio):
    noise_factor = np.random.uniform(0.001, 0.015)
    noise = np.random.randn(len(audio))
    augmented = audio + noise_factor * noise
    return np.clip(augmented, -1.0, 1.0)

def custom_time_stretch(y, rate):
    D = librosa.stft(y)
    D_stretch = librosa.phase_vocoder(D, rate=rate)
    y_stretch = librosa.istft(D_stretch)
    # Подгоняем длину результата к исходной
    if len(y_stretch) > len(y):
        y_stretch = y_stretch[:len(y)]
    else:
        y_stretch = np.pad(y_stretch, (0, len(y) - len(y_stretch)), mode='constant')
    return y_stretch

def augment_time_stretch(audio, sr):
    rate = np.random.uniform(0.8, 1.25)
    return custom_time_stretch(audio, rate)

def custom_pitch_shift(y, sr, n_steps):
    factor = 2.0 ** (n_steps / 12.0)
    y_shifted = librosa.resample(y, orig_sr=sr, target_sr=int(sr * factor))
    y_stretched = custom_time_stretch(y_shifted, 1 / factor)
    if len(y_stretched) > len(y):
        y_stretched = y_stretched[:len(y)]
    else:
        y_stretched = np.pad(y_stretched, (0, len(y) - len(y_stretched)), mode='constant')
    return y_stretched

def augment_pitch_shift(audio, sr):
    n_steps = np.random.uniform(-4, 4)
    return custom_pitch_shift(audio, sr, n_steps)

def augment_shift(audio):
    max_shift_fraction = 0.5
    shift = int(np.random.uniform(-max_shift_fraction, max_shift_fraction) * len(audio))
    return np.roll(audio, shift)

def augment_gain(audio):
    db_change = np.random.uniform(-6, 6)
    factor = 10 ** (db_change / 20)
    augmented = audio * factor
    return np.clip(augmented, -1.0, 1.0)

def augment_echo(audio, sr, delay=0.2, decay=0.5):
    delay_samples = int(delay * sr)
    echo_signal = np.zeros(len(audio) + delay_samples)
    echo_signal[:len(audio)] = audio
    echo_signal[delay_samples:] += decay * audio
    return echo_signal[:len(audio)]

def augment_reverb(audio, sr, reverb_duration=0.3):
    ir_length = int(sr * reverb_duration)
    impulse_response = np.exp(-np.linspace(0, 3, ir_length))
    augmented = np.convolve(audio, impulse_response, mode='full')
    augmented = augmented[:len(audio)]
    max_val = np.max(np.abs(augmented))
    if max_val > 0:
        augmented = augmented / max_val
    return augmented

def augment_distortion(audio):
    gain_factor = np.random.uniform(2.0, 5.0)
    return np.tanh(gain_factor * audio)

def augment_bandpass(audio, sr):
    lowcut = np.random.uniform(200, 500)
    highcut = np.random.uniform(2000, 5000)
    nyq = 0.5 * sr
    low = lowcut / nyq
    high = highcut / nyq
    order = 4
    b, a = butter(order, [low, high], btype='band')
    filtered = lfilter(b, a, audio)
    return filtered

# Список доступных аугментаций (функции принимают audio и sr)
available_augmentations = [
    lambda audio, sr: augment_gaussian_noise(audio),
    lambda audio, sr: augment_time_stretch(audio, sr),
    lambda audio, sr: augment_pitch_shift(audio, sr),
    lambda audio, sr: augment_shift(audio),
    lambda audio, sr: augment_gain(audio),
    lambda audio, sr: augment_echo(audio, sr),
    lambda audio, sr: augment_reverb(audio, sr),
    lambda audio, sr: augment_distortion(audio),
    lambda audio, sr: augment_bandpass(audio, sr)
]

def apply_random_augmentations(audio, sr):
    # Выбираем случайное количество эффектов (например, от 1 до 4)
    chain_length = random.randint(1, 4)
    selected_augs = random.sample(available_augmentations, chain_length)
    augmented_audio = audio.copy()
    for func in selected_augs:
        augmented_audio = func(augmented_audio, sr)
    return augmented_audio

# -----------------------
# Обработка директорий
# -----------------------

def process_directory(directory):
    # Допустимые расширения аудиофайлов
    allowed_exts = {".wav", ".mp3", ".flac", ".ogg", ".aiff", ".aif", ".m4a"}
    # Получаем список файлов в директории
    for filename in os.listdir(directory):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in allowed_exts:
            continue  # пропускаем файлы с неподходящим расширением

        file_path = os.path.join(directory, filename)
        try:
            audio, sr = librosa.load(file_path, sr=None)
        except Exception as e:
            print(f"Ошибка загрузки файла {file_path}: {e}")
            continue

        # Генерируем случайное количество аугментированных версий (от 10 до 20)
        num_variants = random.randint(10, 20)
        print(f"Обработка файла: {file_path} -> генерируется {num_variants} версий")
        for i in range(num_variants):
            try:
                augmented_audio = apply_random_augmentations(audio, sr)
                output_filename = f"{name}_aug{i+1}.wav"
                output_path = os.path.join(directory, output_filename)
                sf.write(output_path, augmented_audio, sr)
                print(f"  Сохранено: {output_path}")
            except Exception as e:
                print(f"  Ошибка при генерации версии {i+1} файла {file_path}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Использование: python augmentation.py <папка1> [папка2] ...")
        return

    directories = sys.argv[1:]
    for directory in directories:
        if not os.path.isdir(directory):
            print(f"'{directory}' не является директорией, пропускаем.")
            continue
        print(f"Обрабатываем директорию: {directory}")
        process_directory(directory)

if __name__ == "__main__":
    main()
