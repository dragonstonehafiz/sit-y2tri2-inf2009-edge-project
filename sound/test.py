import speech_recognition as sr
import time
import os
import onnxruntime as ort
import librosa
import numpy as np
import io

# Parameters
SAMPLE_RATE = 16000
DURATION = 2  # 5 seconds


# Load ONNX Model
def load_model(model_path="bird_sound_model.onnx"):
    session = ort.InferenceSession(model_path)
    for input_info in session.get_inputs():
        print(f"Input Name: {input_info.name}")
        print(f"Input Shape: {input_info.shape}")
        print(f"Input Type: {input_info.type}")
    return session


# Extract Features from Audio (Ensure Mono and Resample to 8000 Hz)
def extract_features(audio_data):
    audio, sr = librosa.load(io.BytesIO(audio_data), sr=SAMPLE_RATE, mono=True)
    # print(f"Audio Sample Rate: {sr}")
    audio_bits = (
        np.iinfo(audio_data[0].dtype).bits if isinstance(audio_data, np.ndarray) else 16
    )
    # print(f"Audio Bit Depth: {audio_bits} bits")
    audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio
    mfccs = librosa.feature.mfcc(y=audio, sr=SAMPLE_RATE, n_mfcc=40)
    mfccs = np.mean(mfccs.T, axis=0).astype(np.float32)
    return mfccs.reshape(1, -1)


# Predict from Audio using ONNX
def predict_from_audio(audio_data, session):
    features = extract_features(audio_data)
    inputs = {session.get_inputs()[0].name: features}
    outputs = session.run(None, inputs)
    print(f"Outputs:{outputs}")
    predicted = np.argmax(outputs[0], axis=1)
    # print(f"Predicted Class: {predicted}")
    label = "bird" if predicted[0] == 0 else "no_bird"
    print(f"Prediction: {label}")


# Recording 5-second Chunks using SpeechRecognition
def record_audio():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            os.system("clear")
        except Exception as e:
            os.system("cls")
        print("Recording 5-second chunks. Press Ctrl+C to stop.")
        while True:
            try:
                audio = recognizer.listen(source, phrase_time_limit=DURATION)
                audio_data = audio.get_wav_data()
                print("Audio chunk captured in memory")
                predict_from_audio(audio_data, session)
            except KeyboardInterrupt:
                print("Recording stopped.")
                break


if __name__ == "__main__":
    session = load_model()
    record_audio()
