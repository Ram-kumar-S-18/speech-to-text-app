import os
import logging
from pathlib import Path

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Whisper Configuration
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))
AUDIO_FORMAT = os.getenv("AUDIO_FORMAT", "wav")

# Server Configuration
PORT = int(os.getenv("PORT", "7860"))
HOST = os.getenv("HOST", "0.0.0.0")

# Output Configuration
_output_dir = os.getenv("OUTPUT_DIR", "")
OUTPUT_DIR = Path(_output_dir) if _output_dir else None

# Temporary Directory
TMP_DIR = os.getenv("TMP_DIR", "tmp")
Path(TMP_DIR).mkdir(exist_ok=True)

# CPU Performance Tuning
WHISPER_CPU_THREADS = int(os.getenv("WHISPER_CPU_THREADS", "4"))
OMP_NUM_THREADS = int(os.getenv("OMP_NUM_THREADS", "4"))

# Log configuration on startup
logger.info(f"Whisper Model: {WHISPER_MODEL_SIZE}")
logger.info(f"Server: {HOST}:{PORT}")
logger.info(f"Sample Rate: {SAMPLE_RATE}Hz, Channels: {CHANNELS}")
logger.info(f"CPU Threads: {WHISPER_CPU_THREADS}, OMP Threads: {OMP_NUM_THREADS}")
