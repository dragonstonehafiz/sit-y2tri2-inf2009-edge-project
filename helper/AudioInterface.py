import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal

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

    def save_waveform(self, audio_data, filename="waveform.png"):
        """
        Saves the waveform of the recorded audio as an image.

        :param audio_data: NumPy array containing recorded audio data.
        :param filename: Name of the output image file.
        """

        plt.figure(figsize=(10, 4))
        time_axis = np.linspace(0, len(audio_data) / self.samplerate, num=len(audio_data))
        plt.plot(time_axis, audio_data, color='blue')
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.title("Waveform of Recorded Audio")
        plt.ylim(-32768, 32767)  # Set limits for 16-bit PCM
        plt.grid()
        plt.savefig(filename)
        plt.close()

    def save_spectrogram(self, audio_data, filename="spectrogram.png"):
        """
        Saves the spectrogram of the recorded audio as an image.

        :param audio_data: NumPy array containing recorded audio data.
        :param filename: Name of the output image file.
        """

        # Compute spectrogram
        f, t, Sxx = scipy.signal.spectrogram(audio_data, fs=self.samplerate, nperseg=1024)
        Sxx_dB = 10 * np.log10(Sxx + 1e-10)  # Adding small value to avoid log(0)
        # Set a threshold (adjust based on your data)
        threshold_dB = np.percentile(Sxx_dB, 95)  # Use 95th percentile as the threshold
        # Find time segments where sound is clearly happening
        sound_active = np.max(Sxx_dB, axis=0) > threshold_dB
        active_time_ranges = t[sound_active]  # Get corresponding time values

        # Plot the spectrogram
        plt.figure(figsize=(10, 4))
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud', cmap='inferno')
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.title("Spectrogram of Recorded Audio")
        plt.colorbar(label="Power (dB)")

        # Save the spectrogram image
        plt.savefig(filename)
        plt.close()

    def close(self):
        self.audio.terminate()


# Example usage:
if __name__ == "__main__":
    audio = AudioInterface()  # Default: samplerate=44100, channels=1

    try:
        while True:
            print("Recording Audio...")
            recorded_audio, peak = audio.record_audio(3)  # Record for 3 seconds

            if recorded_audio is not None:
                print(f"Recorded audio shape: {recorded_audio.shape}")
                print(f"Peak Amplitude: {peak:.4f}")

                # Save waveform image
                audio.save_waveform(recorded_audio)
                audio.save_spectrogram(recorded_audio)
            else:
                print("No audio recorded.")

    except KeyboardInterrupt:
        print("Exiting...")
        audio.close()
