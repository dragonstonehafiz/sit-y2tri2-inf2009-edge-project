import pyaudio
import numpy as np

class AudioInterface:
    def __init__(self, samplerate=44100, channels=1, chunk=1024, device_index=0):
        """
        Initialize the PyAudio interface with sample rate, channels, chunk size, and device index.
        """
        self.samplerate = samplerate
        self.channels = channels
        self.chunk = chunk
        self.format = pyaudio.paInt16  # 16-bit integer format
        self.device_index = device_index  # Set the selected device
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
                                 frames_per_buffer=self.chunk,
                                 input_device_index=self.device_index)  # Use the selected device

        frames = []

        for _ in range(int(self.samplerate / self.chunk * duration)):
            data = stream.read(self.chunk, exception_on_overflow=False)
            frames.append(np.frombuffer(data, dtype=np.int16))

        stream.stop_stream()
        stream.close()

        recorded_audio = np.concatenate(frames, axis=0)
        peak_amplitude = np.max(np.abs(recorded_audio)) / 32767.0  # Normalize peak [0,1]

        return recorded_audio, peak_amplitude

    def close(self):
        self.audio.terminate()



# Example usage:
if __name__ == "__main__":
    # List Devices
    
    p = pyaudio.PyAudio()

    print("Available audio input devices:")

    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev["maxInputChannels"] > 0:  # Only show input devices
            print(f"Index {i}: {dev['name']} - {dev['maxInputChannels']} channels")

    p.terminate()
    
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
