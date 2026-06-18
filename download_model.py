import os
from faster_whisper import download_model

def main():
    model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "models", model_size)
    
    print(f"Downloading faster-whisper '{model_size}' model to: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    path = download_model(model_size, output_dir=output_dir)
    print(f"Successfully downloaded model to: {path}")

if __name__ == "__main__":
    main()
