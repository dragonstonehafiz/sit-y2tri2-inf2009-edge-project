import os
import librosa
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.onnx
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Parameters
DATA_DIR = 'data/' # Path to folder with 'bird' and 'no_bird' subfolders
BATCH_SIZE = 32
EPOCHS = 20
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.mps.is_available() else 'cpu')

# Preprocess Audio to Extract Features in Mono and Resample to 16000 Hz
def extract_features(file_path):
    audio, sr = librosa.load(file_path, mono=True)
    audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    mfccs = librosa.feature.mfcc(y=audio, sr=16000, n_mfcc=40)
    mfccs = np.mean(mfccs.T, axis=0)
    return mfccs

# Prepare Data
def prepare_data():
    labels = []
    features = []
    for label in ['combined', 'no_bird']:
        folder_path = os.path.join(DATA_DIR, label)
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            feature = extract_features(file_path)
            features.append(feature)
            labels.append(label)
    return np.array(features), np.array(labels)

# Load Data
features, labels = prepare_data()

# Encode Labels
label_encoder = LabelEncoder()
labels_encoded = label_encoder.fit_transform(labels)

# Split Data
X_train, X_test, y_train, y_test = train_test_split(features, labels_encoded, test_size=0.2, random_state=42)

# Custom Dataset
class AudioDataset(Dataset):
    def __init__(self, data, labels):
        self.data = torch.tensor(data, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

train_dataset = AudioDataset(X_train, y_train)
test_dataset = AudioDataset(X_test, y_test)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

# Model Creation
class AudioClassifier(nn.Module):
    def __init__(self):
        super(AudioClassifier, self).__init__()
        self.fc1 = nn.Linear(40, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 2)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = AudioClassifier().to(DEVICE)

# Loss and Optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training Loop
def train_model():
    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0.0
        for data, labels in train_loader:
            data, labels = data.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(data)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {total_loss / len(train_loader)}")

# Evaluation
def evaluate_model():
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for data, labels in test_loader:
            data, labels = data.to(DEVICE), labels.to(DEVICE)
            outputs = model(data)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    print(f"Accuracy: {100 * correct / total}%")

# Save Model to ONNX
def save_model_to_onnx():
    model.eval()
    dummy_input = torch.randn(1, 40).to(DEVICE)
    torch.onnx.export(model, dummy_input, 'bird_sound_model.onnx', input_names=['input'], output_names=['output'], opset_version=11)
    print("Model exported to ONNX format as 'bird_sound_model.onnx'")

if __name__ == '__main__':
    # Train and Evaluate
    train_model()
    evaluate_model()
    torch.save(model.state_dict(), 'bird_sound_model.pth')
    print("Model training complete and saved as 'bird_sound_model.pth'")
    save_model_to_onnx()