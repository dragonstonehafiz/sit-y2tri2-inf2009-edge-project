import speech_recognition as sr
import time
import os
import onnxruntime as ort
import librosa
import numpy as np
import io
import time

# Parameters
SAMPLE_RATE = 16000
DURATION = 5  # 5 seconds

# Load ONNX Model
def load_model(model_path='bird_sound_model.onnx'):
    session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    for input_info in session.get_inputs():
        print(f"Input Name: {input_info.name}")
        print(f"Input Shape: {input_info.shape}")
        print(f"Input Type: {input_info.type}")
    return session

# Create interfaces to handle audio
def create_audio_device():
    recognizer = sr.Recognizer()
    source = sr.Microphone(sample_rate=SAMPLE_RATE)
    return source, recognizer

# Extract Features from Audio (Ensure Mono and Resample to 8000 Hz)
def extract_features(audio_data):
    audio, sr = librosa.load(io.BytesIO(audio_data), sr=SAMPLE_RATE, mono=True)
    audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio
    mfccs = librosa.feature.mfcc(y=audio, sr=SAMPLE_RATE, n_mfcc=40)
    mfccs = np.mean(mfccs.T, axis=0).astype(np.float32)
    return mfccs.reshape(1, -1)

# Predict from Audio using ONNX
def predict_from_audio(audio_data, session):
    features = extract_features(audio_data)
    inputs = {session.get_inputs()[0].name: features}
    outputs = session.run(None, inputs)
    predicted = np.argmax(outputs[0], axis=1)
    # print(f"Predicted Class: {predicted}")
    label = 'bird' if predicted[0] == 0 else 'no_bird'
    print(f"Predicted: {label}")
    return predicted[0] == 0

# Recording 5-second Chunks using SpeechRecognition
def record_audio(source, recognizer, duration=5):
    recognizer.adjust_for_ambient_noise(source)
    audio = recognizer.listen(source, phrase_time_limit=duration)
    audio_data = audio.get_wav_data()
    return audio_data
    # os.system('clear')
    # print("Recording 5-second chunks. Press Ctrl+C to stop.")
    # while True:
    #     try:
    #         audio = recognizer.listen(source, phrase_time_limit=duration)
    #         audio_data = audio.get_wav_data()
    #         print("Audio chunk captured in memory")
    #         predict_from_audio(audio_data, session)
    #     except KeyboardInterrupt:
    #         print("Recording stopped.")
    #         break


if __name__ == '__main__':
    print("Loading Model...")
    session = load_model("model/bird_sound_model.onnx")
    time.sleep(2)
    print("Creating Audio Device...")
    recognizer = sr.Recognizer()
    with sr.Microphone(sample_rate=SAMPLE_RATE) as source:
        os.system('clear')
        while True:
            try:
                print(f"Recording sound...")
                audio_data = record_audio(source, recognizer)
                is_bird = predict_from_audio(audio_data, session)
                if is_bird:
                    print("Bird Detected")
                else:
                    print("No Bird Detected")
            except KeyboardInterrupt:
                print("Recording stopped.")
                break
