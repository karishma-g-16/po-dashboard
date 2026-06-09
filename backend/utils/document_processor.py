import os
import logging
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import PIL.Image

# Monkey-patch for easyocr compatibility with modern Pillow (10.0.0+)
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import pandas as pd

logger = logging.getLogger(__name__)

# Initialize EasyOCR Reader Lazily (to prevent slow startup)
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        logger.info("Initializing EasyOCR Reader for the first time...")
        try:
            import easyocr
            # Use CPU by default for broader compatibility; set gpu=True if CUDA is available
            _reader = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
    return _reader

def extract_text_from_file(file_path: str) -> str:
    """
    Unified text extraction from various file formats.
    Aligns Image processing with PDF processing quality.
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
            
            # 2. If no text (scanned PDF), use EasyOCR with enhancement
            if len(text.strip()) < 50:
                logger.info("Scanned PDF detected. Using EasyOCR fallback.")
                reader = get_reader()
                if reader:
                    images = convert_from_path(file_path)
                    for image in images:
                        # Preprocess each page image
                        processed_img = preprocess_image(image)
                        img_np = np.array(processed_img)
                        # Use default grouping (no paragraph) for more granular control
                        result = reader.readtext(img_np, detail=0)
                        # Mark OCR text and strip common table artifacts
                        ocr_raw = " ".join(result)
                        ocr_clean = ocr_raw.replace('|', ' ').replace('!', ' ').replace('[', ' ').replace(']', ' ')
                        text += "[OCR] " + ocr_clean + " "
                else:
                    logger.error("EasyOCR reader not initialized")
        
        elif ext in ['png', 'jpg', 'jpeg']:
            reader = get_reader()
            if reader:
                # 1. Open and Preprocess for high accuracy OCR
                img = Image.open(file_path)
                processed_img = preprocess_image(img)
                
                # 2. Extract RAW text using EasyOCR
                img_np = np.array(processed_img)
                result = reader.readtext(img_np, detail=0)
                # Mark OCR text and strip table artifacts
                ocr_raw = " ".join(result)
                ocr_clean = ocr_raw.replace('|', ' ').replace('!', ' ').replace('[', ' ').replace(']', ' ')
                text = "[OCR] " + ocr_clean
                
                # 3. Handle common OCR artifacts (Shared with PDF logic)
                text = text.replace('\ufffd', '₹').replace('ī', '₹').replace('?', '₹')
            else:
                logger.error("EasyOCR reader not initialized")
        
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
    Advanced image preprocessing for high-accuracy OCR on screenshots and photos.
    Optimized for SPEED: Resizes to 1600px, heavily reducing CPU load while maintaining accuracy.
    Includes autocontrast for uneven lighting and optimized sharpening.
    """
    # 1. Resize for OCR (1600px width is optimal for speed vs accuracy balance)
    width, height = img.size
    target_width = 1600
    if width > target_width:
        # Scale DOWN if too large (saves massive processing time)
        scale = target_width / width
        img = img.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
    elif width < target_width:
        # Scale UP if too small
        scale = target_width / width
        img = img.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
    
    # 2. Handle lighting/exposure (Crucial for photos of paper)
    img = ImageOps.autocontrast(img)
    
    # 3. Convert to high-contrast Grayscale
    img = img.convert('L')
    
    # 4. Enhance contrast and sharpness moderately
    img = ImageEnhance.Contrast(img).enhance(1.8)
    img = ImageEnhance.Sharpness(img).enhance(1.2)
    
    return img
