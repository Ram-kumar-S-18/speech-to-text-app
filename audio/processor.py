import subprocess
import tempfile
import numpy as np
import soundfile as sf
from config import SAMPLE_RATE

MIN_RMS = 0.003


class AudioProcessor:
    @staticmethod
    def convert_to_wav(input_path: str) -> str:
        out = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        out_path = out.name
        out.close()
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", input_path,
             "-ar", str(SAMPLE_RATE), "-ac", "1",
             "-sample_fmt", "s16",
             out_path],
            capture_output=True, timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr.decode()}")
        return out_path

    @staticmethod
    def has_valid_audio(wav_path: str) -> bool:
        try:
            data, sr = sf.read(wav_path)
            if len(data) < int(sr * 0.3):
                return False
            rms = np.sqrt(np.mean(data ** 2))
            return rms >= MIN_RMS
        except Exception:
            return True

    def preprocess(self, audio_path: str) -> str:
        wav = self.convert_to_wav(audio_path)
        try:
            data, sr = sf.read(wav)
            if len(data) < int(sr * 0.3):
                raise ValueError("Recording too short.")
            rms = np.sqrt(np.mean(data ** 2))
            if rms == 0.0:
                raise ValueError("Microphone is recording complete silence. Please check if your mic is muted or if the correct input device is selected in your OS/browser.")
            elif rms < MIN_RMS:
                raise ValueError("No speech detected. Speak louder or closer to mic.")
        except ValueError as e:
            raise e
        except Exception:
            pass
        return wav
