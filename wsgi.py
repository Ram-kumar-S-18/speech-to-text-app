#!/usr/bin/env python3
"""
WSGI entry point for Gunicorn in production environments.
Preloads the Whisper model to ensure it's available for all worker processes.
"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import and configure
import config
from ui.app import DictateApp
from transcription.whisper_stt import WhisperTranscriber

# Preload Whisper model
model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
config.logger.info(f"Preloading Whisper model '{model_size}' for production...")
WhisperTranscriber.load(model_size)

# Create app instance for Gunicorn
app_instance = DictateApp(tmp_dir=config.TMP_DIR)
app = app_instance.app

if __name__ == "__main__":
    # For local testing only
    app_instance.launch(host=config.HOST, port=config.PORT)

