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
            print(f"Loading faster-whisper '{size}' (int8 CPU, threads={threads})...")
            cls._model = WhisperModel(size, device="cpu", compute_type="int8", cpu_threads=threads)
            cls._model_size = size
            print("Model ready.")
        return cls._model

    def transcribe(self, audio_path: str, model_size: str = None) -> dict:
        model = self.load(model_size)
        segments, info = model.transcribe(
            audio_path,
            beam_size=1,
            vad_filter=True,
            temperature=0.0,
        )
        text = " ".join(seg.text for seg in segments)
        lang = info.language if info else "en"
        return {"text": text.strip(), "language": lang}
