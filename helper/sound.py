import librosa
import numpy as np
import onnxruntime as ort
import sounddevice as sd
import queue

# Parameters
SAMPLE_RATE = 22050
DURATION = 5  # 5 seconds

# Audio Capture
q = queue.Queue()
def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(indata.copy())

# Load ONNX Model
def load_model(model_path='bird_sound_model.onnx'):
    session = ort.InferenceSession(model_path)
    return session

# Extract Features from Audio
def extract_features(audio):
    mfccs = librosa.feature.mfcc(y=audio, sr=SAMPLE_RATE, n_mfcc=40)
    mfccs = np.mean(mfccs.T, axis=0).astype(np.float32)
    return mfccs.reshape(1, -1)

# Predict from Audio using ONNX
def predict_from_audio(audio, session):
    features = extract_features(audio)
    inputs = {session.get_inputs()[0].name: features}
    outputs = session.run(None, inputs)
    print("Outputs:", outputs)
    predicted = np.argmax(outputs[0], axis=1)
    label = 'bird' if predicted[0] == 0 else 'no_bird'
    print(f"Prediction: {label}")

# Capture and Predict Audio
def capture_and_predict(session):
    print("Recording... Speak now!")
    with sd.InputStream(callback=callback, channels=1, samplerate=SAMPLE_RATE):
        audio_data = []
        while len(audio_data) < SAMPLE_RATE * DURATION:
            audio_data.extend(q.get().flatten())
        print("Recording complete.")
        audio_data = np.array(audio_data)
        predict_from_audio(audio_data, session)

if __name__ == '__main__':
    session = load_model()
    capture_and_predict(session)
