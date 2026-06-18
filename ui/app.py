import os
import uuid
import base64
import time
from pathlib import Path
from flask import Flask, jsonify, render_template, request

from audio.processor import AudioProcessor
from transcription.whisper_stt import WhisperTranscriber
from transcription.corrector import TranscriptCorrector


class DictateApp:
    def __init__(self, tmp_dir="tmp"):
        self.tmp_dir = Path(tmp_dir)
        self.tmp_dir.mkdir(exist_ok=True)
        self.processor = AudioProcessor()
        self.transcriber = WhisperTranscriber()
        self.corrector = TranscriptCorrector()
        
        # Initialize Flask to resolve template and static folders relative to this script
        self.app = Flask(__name__, template_folder="templates", static_folder="static")

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/x", methods=["POST", "OPTIONS"])
        def transcribe():
            if request.method == "OPTIONS":
                response = self.app.make_response("")
                origin = request.headers.get("Origin")
                response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
                response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type"
                response.headers["Access-Control-Max-Age"] = "86400"
                return response

            t0 = time.time()
            webm = None
            wav = None
            try:
                data = request.get_json()
                b64 = data.get("a", "")
                model_size = data.get("model")
                use_corrector = data.get("correct", True)
                if not b64:
                    return jsonify({"ok": False, "error": "No audio data"})

                raw = base64.b64decode(b64)
                if len(raw) < 500:
                    return jsonify({"ok": False, "error": "Recording too short"})

                uid = uuid.uuid4().hex
                webm = self.tmp_dir / f"{uid}.webm"
                webm.write_bytes(raw)

                t1 = time.time()
                wav = self.processor.preprocess(str(webm))
                t2 = time.time()
                result = self.transcriber.transcribe(wav, model_size=model_size)
                t3 = time.time()
                if use_corrector:
                    corrected = self.corrector.correct(result.get("text", ""))
                else:
                    corrected = result.get("text", "")
                t4 = time.time()

                elapsed = time.time() - t0
                print(f"  total={elapsed:.1f}s [audio={t2-t1:.1f}s + whisper={t3-t2:.1f}s + correct={t4-t3:.2f}s]")
                print(f"  text: \"{corrected[:80]}\"")

                return jsonify({"ok": True, "text": corrected, "time": round(elapsed, 1)})

            except ValueError as e:
                return jsonify({"ok": False, "error": str(e)})
            except Exception as e:
                return jsonify({"ok": False, "error": f"Server error: {str(e)}"})
            finally:
                for p_var in [webm, wav]:
                    if p_var:
                        p = Path(p_var)
                        if p.exists():
                            try:
                                p.unlink()
                            except Exception:
                                pass

        @self.app.after_request
        def add_security_headers(response):
            # Production Hardening Headers
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' https://fonts.googleapis.com 'unsafe-inline' https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
                "connect-src 'self' https://speech-to-text-app-5kuv.onrender.com; "
                "img-src 'self' data:; "
                "media-src 'self' blob:;"
            )
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Permissions-Policy"] = "microphone=(self)"

            # CORS headers for actual responses
            origin = request.headers.get("Origin")
            response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
            response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"

            return response

    def launch(self, host="0.0.0.0", port=7865):
        print(f"  Open: http://{host}:{port}")
        use_waitress = os.getenv("WAITRESS", "1") == "1"
        if use_waitress:
            from waitress import serve
            serve(self.app, host=host, port=port)
        else:
            self.app.run(host=host, port=port, debug=False)
