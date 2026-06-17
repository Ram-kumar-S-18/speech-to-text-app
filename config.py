import os
from pathlib import Path

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))
AUDIO_FORMAT = os.getenv("AUDIO_FORMAT", "wav")

PORT = int(os.getenv("PORT", "7865"))
HOST = os.getenv("HOST", "0.0.0.0")

_output_dir = os.getenv("OUTPUT_DIR", "")
OUTPUT_DIR = Path(_output_dir) if _output_dir else None

TMP_DIR = os.getenv("TMP_DIR", "tmp")
