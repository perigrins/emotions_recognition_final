import os
import shutil
import numpy as np
import librosa
import tensorflow as tf
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation


# Ścieżki do plików
sad_dir = r'C:\Users\hania\OneDrive\Desktop\Recorded\sad'
happy_dir = r'C:\Users\hania\OneDrive\Desktop\Recorded\happy'
test_dir = r'C:\Users\hania\OneDrive\Desktop\Recorded\test_samples'

# Utwórz folder test_samples, jeśli nie istnieje
os.makedirs(test_dir, exist_ok=True)

# Funkcja do kopiowania plików i zmiany nazw
def copy_and_rename(src_dir, dest_dir, emotion):
    files = [f for f in os.listdir(src_dir) if f.endswith('.wav')]
    if files:
        src_file = os.path.join(src_dir, files[0])
        dest_file = os.path.join(dest_dir, f'test_{emotion}.wav')
        shutil.copy(src_file, dest_file)
        return dest_file
    return None

# Kopiuj pliki i usuń etykiety emocji z nazw
sad_test_file = copy_and_rename(sad_dir, test_dir, 'sad')
happy_test_file = copy_and_rename(happy_dir, test_dir, 'happy')

# Funkcja do ekstrakcji cech
def extract_features(file_name):
    try:
        audio, sample_rate = librosa.load(file_name, sr=22050)
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        mfccs_processed = np.mean(mfccs.T, axis=0)
    except Exception as e:
        print(f"Error encountered while parsing file: {file_name}. Error: {e}")
        return None
    return mfccs_processed

# Przygotowanie danych
def load_data(directory, label):
    features, labels = [], []
    for subdir, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.wav'):
                file_path = os.path.join(subdir, file)
                data = extract_features(file_path)
                if data is not None:
                    features.append(data)
                    labels.append(label)
    return np.array(features), np.array(labels)

# Wczytanie danych z folderów smutku i radości
X_sad, y_sad = load_data(sad_dir, 0)  # 0 dla smutku
X_happy, y_happy = load_data(happy_dir, 1)  # 1 dla radości

# Połączenie danych
X = np.concatenate((X_sad, X_happy), axis=0)
y = np.concatenate((y_sad, y_happy), axis=0)

# Podział na zbiory treningowe i testowe
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Budowa modelu
model = Sequential()
model.add(Dense(256, input_shape=(40,)))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(128))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(2))  # 2 klasy: smutek i radość
model.add(Activation('softmax'))
model.compile(loss='sparse_categorical_crossentropy', metrics=['accuracy'], optimizer='adam')

# Trening modelu
model.fit(X_train, y_train, batch_size=32, epochs=50, validation_data=(X_test, y_test), verbose=1)

# Ewaluacja modelu
score = model.evaluate(X_test, y_test, verbose=0)
print(f'Test loss: {score[0]} / Test accuracy: {score[1]}')

# Funkcja do przewidywania emocji na podstawie pliku audio
def predict_emotion(file_path):
    features = extract_features(file_path)
    if features is not None:
        features = np.expand_dims(features, axis=0)
        prediction = model.predict(features)
        predicted_emotion = np.argmax(prediction)
        emotion_label = 'Happy' if predicted_emotion == 1 else 'Sad'
        return emotion_label
    return None

# Funkcja do przetwarzania pliku audio
def process_audio(filepath):
    # Przewiduj emocje dla danego pliku audio
    emotion = predict_emotion(filepath)
    return emotion

# Wyświetlanie wyników testowych
print(f"Emotion for {os.path.basename(sad_test_file)}: {predict_emotion(sad_test_file)}")
print(f"Emotion for {os.path.basename(happy_test_file)}: {predict_emotion(happy_test_file)}")