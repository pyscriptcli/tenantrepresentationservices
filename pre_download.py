# pre_download.py
import easyocr
import sys

print("Starting EasyOCR model download...")
try:
    # Initialize the reader to trigger the model download
    # We download English by default. Add others if needed.
    easyocr.Reader(['en'], gpu=False, download_enabled=True)
    print("Models downloaded successfully!")
except Exception as e:
    print(f"Failed to download models: {e}")
    sys.exit(1)
