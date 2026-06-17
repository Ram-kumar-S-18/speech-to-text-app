import time
import hashlib
from pathlib import Path

from config import OUTPUT_DIR


def timestamp_filename(prefix="recording", ext=".wav"):
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = OUTPUT_DIR or Path("outputs")
    out.mkdir(parents=True, exist_ok=True)
    return out / f"{prefix}_{ts}{ext}"


def get_file_hash(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"
