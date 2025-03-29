# Bird Sound Classification

This project provides a complete pipeline for detecting bird sounds in audio clips. It includes tools for preprocessing, training a machine learning model, and real-time prediction.

## Project Structure

```
.
├── split_audio.py   # Preprocess audio by splitting and mixing
├── train.py         # Train an audio classification model
├── test.py          # Real-time prediction using microphone + ONNX model
├── bird_sound_model.pth / .onnx  # (generated) trained model
└── data/
    ├── bird/         # 5s chunks of bird sounds
    ├── no_bird/      # 5s chunks of non-bird sounds
    ├── combined/     # no_bird with random bird overlays
    └── *.wav / *.m4a # Input audio files
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Step-by-Step Usage

### 1. Preprocess Audio

Split full-length audio into 5-second chunks and overlay bird sounds randomly:

```bash
python split_audio.py
```

Make sure your input audio files are placed in:

- `data/bird.wav`
- `data/no_bird_new.m4a`

Outputs will be saved in `data/bird/`, `data/no_bird/`, and `data/combined/`.

### 2. Train the Model

Train a classifier on the preprocessed audio:

```bash
python train.py
```

This will:
- Train a simple neural network using MFCC features
- Save the model in PyTorch (`bird_sound_model.pth`) and ONNX (`bird_sound_model.onnx`) formats
- Print accuracy on the validation set

### 3. Test / Predict in Real Time

Run live audio classification using your microphone:

```bash
python test.py
```

This loads the ONNX model and classifies 5-second audio chunks in real-time.

## Model Input Details

- Input Features: 40-dimensional MFCCs
- Sample Rate: 16kHz
- Clip Duration: 5 seconds
- Classes: `bird`, `no_bird`

## Notes

- You can extend this with better models (CNNs, transformers) or augmentations.
- Use higher quality audio and more data for better accuracy.
