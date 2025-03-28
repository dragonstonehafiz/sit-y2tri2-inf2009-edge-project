import os
import librosa
import soundfile as sf
import numpy as np
import random


def split_audio(file_path, output_dir, chunk_duration=5):
    """
    Split an audio file into smaller chunks.

    Parameters:
    file_path (str): Path to the input audio file (.wav).
    output_dir (str): Directory to save the output chunks.
    chunk_duration (int): Duration of each chunk in seconds.
    """
    # Load audio
    audio, sr = librosa.load(file_path, sr=None)
    total_samples = len(audio)
    chunk_samples = int(chunk_duration * sr)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Split and save chunks
    for i, start_sample in enumerate(range(0, total_samples, chunk_samples)):
        end_sample = min(start_sample + chunk_samples, total_samples)
        chunk = audio[start_sample:end_sample]
        output_path = os.path.join(output_dir, f"chunk_{i+1}.wav")
        sf.write(output_path, chunk, sr)
        print(f"Saved {output_path}")


def overlay_random_bird_sound(no_bird_dir, bird_dir, output_dir):
    """
    Randomly overlay bird sounds over no bird sounds.

    Parameters:
    no_bird_dir (str): Path to the directory with no bird sound chunks.
    bird_dir (str): Path to the directory with bird sound chunks.
    output_dir (str): Path to save the output with overlaid sounds.
    """
    os.makedirs(output_dir, exist_ok=True)

    no_bird_files = [
        os.path.join(no_bird_dir, f)
        for f in os.listdir(no_bird_dir)
        if f.endswith(".wav")
    ]
    bird_files = [
        os.path.join(bird_dir, f) for f in os.listdir(bird_dir) if f.endswith(".wav")
    ]

    for i, no_bird_file in enumerate(no_bird_files):
        no_bird_audio, sr = librosa.load(no_bird_file, sr=None)
        bird_file = random.choice(bird_files)
        bird_audio, _ = librosa.load(bird_file, sr=sr)

        # Trim or pad bird sound to match no_bird sound length
        if len(bird_audio) > len(no_bird_audio):
            bird_audio = bird_audio[: len(no_bird_audio)]
        else:
            bird_audio = np.pad(bird_audio, (0, len(no_bird_audio) - len(bird_audio)))

        # Overlay sounds
        combined_audio = no_bird_audio + bird_audio
        combined_audio = np.clip(combined_audio, -1.0, 1.0)

        output_path = os.path.join(output_dir, f"combined_{i+1}.wav")
        sf.write(output_path, combined_audio, sr)
        print(f"Saved {output_path}")


if __name__ == "__main__":
    input_audio_path_bird = "data/bird.wav"  # Path to input audio
    bird_sound_directory = "data/bird"  # Path to bird sounds
    input_audio_path_no_bird = "data/no_bird_new.m4a"  # Path to input audio
    no_bird_sound_directory = "data/no_bird"  # Path to save chunks
    combined_output_directory = "data/combined"  # Path to save combined sounds

    split_audio(input_audio_path_bird, bird_sound_directory, chunk_duration=5)
    print("Audio split bird complete.")

    # Split no bird sound into chunks
    split_audio(input_audio_path_no_bird, no_bird_sound_directory, chunk_duration=5)
    print("Audio split no bird complete.")

    # Overlay bird sounds randomly
    overlay_random_bird_sound(
        no_bird_sound_directory, bird_sound_directory, combined_output_directory
    )
    print("Overlay complete.")
