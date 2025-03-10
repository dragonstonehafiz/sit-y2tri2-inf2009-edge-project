import pyaudio
import numpy as np

class AudioInterface:
    def __init__(self, samplerate=44100, channels=1, chunk=1024):
        """
        Initialize the PyAudio interface with sample rate, channels, and chunk size.
        """
        self.samplerate = samplerate
        self.channels = channels
        self.chunk = chunk
        self.format = pyaudio.paInt16  # Use 16-bit integer format
        self.audio = pyaudio.PyAudio()  # Initialize PyAudio

    def record_audio(self, duration=3):
        """
        Records audio using PyAudio for a specified duration and calculates the peak amplitude.

        :param duration: Recording duration in seconds.
        :return: Tuple (NumPy array containing recorded audio data, peak amplitude)
        """
        stream = self.audio.open(format=self.format,
                                 channels=self.channels,
                                 rate=self.samplerate,
                                 input=True,
                                 frames_per_buffer=self.chunk)

        frames = []

        for _ in range(int(self.samplerate / self.chunk * duration)):
            data = stream.read(self.chunk, exception_on_overflow=False)
            frames.append(np.frombuffer(data, dtype=np.int16))

        # Close the stream
        stream.stop_stream()
        stream.close()

        # Convert recorded data to a single NumPy array
        recorded_audio = np.concatenate(frames, axis=0)

        # Compute Peak Amplitude
        peak_amplitude = np.max(np.abs(recorded_audio)) / 32767.0  # Normalize peak to range [0,1]

        return recorded_audio, peak_amplitude

    def close(self):
        self.audio.terminate()


# Example usage:
if __name__ == "__main__":
    audio = AudioInterface()  # Default: samplerate=44100, channels=1

    try:
        while True:
            print("Recording Audio...")
            recorded_audio, peak = audio.record_audio(1)  # Record for 3 seconds

            if recorded_audio is not None:
                print(f"Recorded audio shape: {recorded_audio.shape}")
                print(f"Peak Amplitude: {peak:.4f}")
            else:
                print("No audio recorded.")

    except KeyboardInterrupt:
        print("Exiting...")
        audio.close()
