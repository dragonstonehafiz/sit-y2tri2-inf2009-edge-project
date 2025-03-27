import speech_recognition as sr
import time
import os
import onnxruntime as ort
import librosa
import numpy as np

# Parameters
SAMPLE_RATE = 22050
DURATION = 5  # 5 seconds

# Load ONNX Model
def load_model(model_path='bird_sound_model.onnx'):
    session = ort.InferenceSession(model_path)
    for input_info in session.get_inputs():
        print(f"Input Name: {input_info.name}")
        print(f"Input Shape: {input_info.shape}")
        print(f"Input Type: {input_info.type}")
    return session

# Extract Features from Audio
def extract_features(file_path):
    audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)
    audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio
    mfccs = librosa.feature.mfcc(y=audio, sr=SAMPLE_RATE, n_mfcc=40)
    mfccs = np.mean(mfccs.T, axis=0).astype(np.float32)
    return mfccs.reshape(1, -1)

# Predict from Audio using ONNX
def predict_from_audio(file_path, session):
    features = extract_features(file_path)
    inputs = {session.get_inputs()[0].name: features}
    outputs = session.run(None, inputs)
    predicted = np.argmax(outputs[0], axis=1)
    label = 'bird' if predicted[0] == 0 else 'no_bird'
    print(f"Prediction: {label}")

# Recording 5-second Chunks using SpeechRecognition
def record_audio(output_file='input.wav'):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        os.system('clear')
        print("Recording 5-second chunks. Press Ctrl+C to stop.")
        while True:
            try:
                audio = recognizer.listen(source, phrase_time_limit=DURATION)
                with open(output_file, "wb") as f:
                    f.write(audio.get_wav_data())
                print("Audio chunk saved to input.wav")
                predict_from_audio(output_file, session)
            except KeyboardInterrupt:
                print("Recording stopped.")
                break

if __name__ == '__main__':
    session = load_model()
    record_audio()
