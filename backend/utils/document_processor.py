import os
import logging
# import numpy as np
# from PIL import Image, ImageOps, ImageEnhance
# import PIL.Image
# import pytesseract

# # Monkey-patch for pytesseract compatibility with modern Pillow (10.0.0+)
# if not hasattr(PIL.Image, 'ANTIALIAS'):
#     PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# from pdf2image import convert_from_path
# from PyPDF2 import PdfReader
# import pandas as pd

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: str) -> str:
    """
    STUBBED: Unified text extraction is currently disabled to bypass Render build issues.
    """
    ext = file_path.split('.')[-1].lower()
    text = f"STUBBED CONTENT for {ext}"
    
    try:
        if ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
    except Exception as e:
        logger.error(f"Extract error: {e}")
    
    return text

def preprocess_image(img):
    """STUBBED"""
    return img
