import sys
from PIL import Image
from backend.utils.document_processor import preprocess_image
import easyocr
import numpy as np

reader = easyocr.Reader(['en'], gpu=False)

def test_img(path):
    try:
        img = Image.open(path)
        processed = preprocess_image(img)
        img_np = np.array(processed)
        result = reader.readtext(img_np, detail=0)
        print(f"--- {path} ---")
        print(" ".join(result))
        print()
    except Exception as e:
        print(f"Failed to process {path}: {e}")

test_img(r"C:\Users\karis\Downloads\WhatsApp Image 2026-06-04 at 10.17.03 AM.jpeg")
test_img(r"C:\Users\karis\Downloads\WhatsApp Image 2026-06-03 at 11.46.14 AM.jpeg")
test_img(r"C:\Users\karis\Downloads\WhatsApp Image 2026-06-03 at 11.46.13 AM.jpeg")
