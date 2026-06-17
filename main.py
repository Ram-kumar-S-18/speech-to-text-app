#!/usr/bin/env python3
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import DictateApp


def main():
    from config import WHISPER_MODEL_SIZE, PORT, HOST
    parser = argparse.ArgumentParser(description="Speech-to-Text Converter")
    parser.add_argument("--port", type=int, default=PORT,
                        help=f"Port (default: {PORT})")
    parser.add_argument("--host", type=str, default=HOST,
                        help=f"Host (default: {HOST})")
    parser.add_argument("--model", type=str, default=WHISPER_MODEL_SIZE,
                        help="Whisper model: tiny/base/small/medium/large")
    args = parser.parse_args()

    import config
    config.WHISPER_MODEL_SIZE = args.model

    from transcription.whisper_stt import WhisperTranscriber
    print(f"Pre-loading whisper '{args.model}'...")
    WhisperTranscriber.load(args.model)

    app = DictateApp(tmp_dir=config.TMP_DIR)
    app.launch(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
