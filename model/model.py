import librosa
import numpy as np
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models
from tqdm import tqdm
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.models import load_model

classes = [
    #  'chicken', 'child', 'evil', 'friendly', 'magical', 'non_human', 'pirate', 'poor', 'poor2', 'rich', 'witch_clown',
           'evil','poor','rich','witch_clown']

def build_model_cnn(input_shape, num_classes):
    model = models.Sequential([
        # Блок 1
        layers.Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.3),  # регуляризация

        # Блок 2
        layers.Conv2D(64, (3, 3), padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.4),

        # Блок 3 (можно добавлять ещё при желании)
        layers.Conv2D(128, (3, 3), padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.4),

        # Выход
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy']
    )
    return model

def load_data(data_path, sr=16000, duration=5):
    X = []
    y = []
    # classes = sorted(os.listdir(data_path))
    for label, cls in tqdm(enumerate(classes), desc='Classes'):
        cls_folder = os.path.join(data_path, cls)
        if not os.path.isdir(cls_folder):
            continue
        for fname in tqdm(os.listdir(cls_folder), desc=cls):
            if not fname.endswith('.wav'):
                continue
            fpath = os.path.join(cls_folder, fname)

            desired_len = sr * duration
            audio, _ = librosa.load(fpath, sr=sr)
            if len(audio) < desired_len:
                audio = librosa.util.fix_length(data=audio, size=desired_len)
            else:
                audio = audio[:desired_len]
            # извлечения Mel-спектрограммы
            melspec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=64)
            # Конвертируем в dB
            melspec_db = librosa.power_to_db(melspec, ref=np.max)
            X.append(melspec_db)
            y.append(label)
    X = np.array(X)
    y = np.array(y)
    return X, y, classes

current_dir = os.path.dirname(os.path.abspath(__file__))
sr = 16000
duration = 5
n_mels = 64

def audio_to_melspec_db(file_path):
    audio, _ = librosa.load(file_path, sr=sr)
    # обрезаем/дополняем до 5 сек
    desired_len = sr * duration
    audio = librosa.util.fix_length(data=audio, size=desired_len)
    
    # Mel-спектрограмма
    melspec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=n_mels)
    melspec_db = librosa.power_to_db(melspec, ref=np.max)
    return melspec_db

def softmax(x):
    exp_x = np.exp(x - np.max(x))
    return exp_x / exp_x.sum(axis=-1, keepdims=True)

def predict_class(audio_path):
    test_melspec = audio_to_melspec_db(audio_path)
    test_melspec = test_melspec[np.newaxis, ..., np.newaxis]  # shape (1, 64, time, 1)
    model = load_model(os.path.join(current_dir,'models') +'/'+'_'.join(classes)+'.keras')
    pred = model.predict(test_melspec)
    
    probabilities = softmax(pred)
    percentages = pred[0]

    return {classes[class_id]:percent for class_id, percent in enumerate(percentages)}

if __name__ == "__main__":
    # кешируем что б каждий раз не обрабатывать данные надо чистить если меняется содержимое папки audio
    data_path = os.path.join(current_dir,'audio')
    data_path_classes = os.path.join(current_dir,'models') +'/'+'_'.join(classes)+'.npz'
    if (os.path.exists(data_path_classes)):
        data = np.load(data_path_classes, allow_pickle=True)
        X = data['X']
        y = data['y']
        class_names = data['class_names']
    else:
        X, y, class_names = load_data(data_path)
        np.savez(data_path_classes, X=X, y=y, class_names=class_names)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1, random_state=42)

    X_train = X_train[..., np.newaxis]  # (кол-во образцов, частотные полосы, временные фреймы, 1)
    X_val = X_val[..., np.newaxis]

    early_stop = EarlyStopping(
        monitor='val_accuracy',
        patience=10,
        restore_best_weights=True,
        verbose=1
    )

    model_1_checkpoint = ModelCheckpoint(
        filepath=os.path.join(current_dir,'models') +'/'+'_'.join(classes)+'.keras',
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )

    if (os.path.exists(os.path.join(current_dir,'models') +'/'+'_'.join(classes)+'.keras')):
        model1 = load_model(os.path.join(current_dir,'models') +'/'+'_'.join(classes)+'.keras')
    else:
        model1 = build_model_cnn(X_train.shape[1:], len(class_names))
        model1.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, callbacks=[early_stop, model_1_checkpoint])
