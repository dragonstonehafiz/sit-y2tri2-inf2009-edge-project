import sounddevice as sd
import numpy as np

class AudioInterface:
    def __init__(self, samplerate=44100, channels=1):
        """
        Initialize the audio interface with default sample rate and channels.
        """
        self.samplerate = samplerate
        self.channels = channels

    def record_audio(self, duration=3):
        """
        Records audio for a specified duration and calculates the peak amplitude.

        :param duration: Recording duration in seconds.
        :return: Tuple (NumPy array containing recorded audio data, peak amplitude)
        """
        try:
            recorded_audio = sd.rec(
                int(duration * self.samplerate), 
                samplerate=self.samplerate, 
                channels=self.channels, 
                dtype=np.float32
            )
            sd.wait()  # Block until recording is finished

            # Compute Peak Amplitude (max absolute value)
            peak_amplitude = np.max(np.abs(recorded_audio))

            return recorded_audio, peak_amplitude
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None, None

# Example usage:
if __name__ == "__main__":
    audio = AudioInterface()  # Default: samplerate=44100, channels=1

    while True:
        try:
            print("Recording Audio")
            recorded_audio, peak = audio.record_audio(3)  # Record for 3 seconds

            if recorded_audio is not None:
                print(f"Recorded audio shape: {recorded_audio.shape}")
                print(f"Peak Amplitude: {peak:.4f}")
            else:
                print("No audio recorded.")
        except KeyboardInterrupt as e:
            print("Exiting")
            break
