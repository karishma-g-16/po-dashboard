import os
import logging
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import PIL.Image
import pytesseract

# Monkey-patch for pytesseract compatibility with modern Pillow (10.0.0+)
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import pandas as pd

logger = logging.getLogger(__name__)

# Configure Tesseract path if needed (for local Windows dev)
# In Render (Linux), it will be in the system path automatically.
if os.name == 'nt': # Windows
    tess_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tess_path):
        pytesseract.pytesseract.tesseract_cmd = tess_path

def extract_text_from_file(file_path: str) -> str:
    """
    Unified text extraction from various file formats using Tesseract OCR.
    Tesseract is used instead of EasyOCR to save memory (Render 512MB limit).
    """
    ext = file_path.split('.')[-1].lower()
    text = ""
    
    try:
        if ext == 'pdf':
            # 1. Try digital text extraction first
            try:
                pdf_reader = PdfReader(file_path)
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted: text += extracted + " "
            except Exception as e:
                logger.warning(f"Digital PDF extraction failed: {e}")
            
            # 2. If no text (scanned PDF), use Tesseract fallback
            if len(text.strip()) < 50:
                logger.info("Scanned PDF detected. Using Tesseract fallback.")
                images = convert_from_path(file_path)
                for image in images:
                    # Preprocess each page image
                    processed_img = preprocess_image(image)
                    # Extract text using Tesseract
                    ocr_text = pytesseract.image_to_string(processed_img)
                    text += "[OCR] " + ocr_text + " "
        
        elif ext in ['png', 'jpg', 'jpeg']:
            # 1. Open and Preprocess
            img = Image.open(file_path)
            processed_img = preprocess_image(img)
            
            # 2. Extract text using Tesseract
            ocr_text = pytesseract.image_to_string(processed_img)
            text = "[OCR] " + ocr_text
            
            # 3. Clean common artifacts
            text = text.replace('\ufffd', '₹').replace('ī', '₹').replace('?', '₹')
        
        elif ext in ['xlsx', 'xls']:
            df = pd.read_excel(file_path)
            text = df.to_string()
        
        elif ext == 'csv':
            df = pd.read_csv(file_path)
            text = df.to_string()
        
        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
    
    except Exception as e:
        logger.error(f"Extract error: {e}")
    
    return text

def preprocess_image(img: Image.Image) -> Image.Image:
    """
    Advanced image preprocessing optimized for Tesseract OCR.
    Resizes, converts to grayscale, and enhances contrast.
    """
    # 1. Resize for OCR (2000px width is good for Tesseract)
    width, height = img.size
    target_width = 2000
    if width != target_width:
        scale = target_width / width
        img = img.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
    
    # 2. Handle lighting/exposure
    img = ImageOps.autocontrast(img)
    
    # 3. Convert to Grayscale
    img = img.convert('L')
    
    # 4. Enhance contrast and sharpness
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    
    return img
