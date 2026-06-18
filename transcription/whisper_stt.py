from faster_whisper import WhisperModel
from config import WHISPER_MODEL_SIZE


class WhisperTranscriber:
    _model = None
    _model_size = None

    @classmethod
    def load(cls, model_size: str = None):
        import os
        size = model_size or WHISPER_MODEL_SIZE
        if cls._model is None or cls._model_size != size:
            threads = int(os.getenv("WHISPER_CPU_THREADS", os.getenv("OMP_NUM_THREADS", "4")))
            # Check for local pre-downloaded model
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            local_model_path = os.path.join(current_dir, "models", size)
            if os.path.exists(local_model_path):
                print(f"Loading faster-whisper '{size}' from local path '{local_model_path}' (int8 CPU, threads={threads})...")
                cls._model = WhisperModel(local_model_path, device="cpu", compute_type="int8", cpu_threads=threads)
            else:
                print(f"Loading faster-whisper '{size}' from hub (int8 CPU, threads={threads})...")
                cls._model = WhisperModel(size, device="cpu", compute_type="int8", cpu_threads=threads)
            cls._model_size = size
            print("Model ready.")
        return cls._model

    def transcribe(self, audio_path: str, model_size: str = None) -> dict:
        model = self.load(model_size)
        try:
            segments, info = model.transcribe(
                audio_path,
                beam_size=1,
                vad_filter=True,
                temperature=0.0,
            )
            text = " ".join(seg.text for seg in segments)
            lang = info.language if info else "en"
            return {"text": text.strip(), "language": lang}
        except ValueError as e:
            if "max() arg is an empty sequence" in str(e):
                return {"text": "", "language": "en"}
            raise e
