import os
import logging
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import easyocr
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import pandas as pd

logger = logging.getLogger(__name__)

# Initialize EasyOCR Reader (loads once into memory)
try:
    # Use CPU by default for broader compatibility; set gpu=True if CUDA is available
    reader = easyocr.Reader(['en'], gpu=False)
except Exception as e:
    logger.error(f"Failed to initialize EasyOCR: {e}")
    reader = None

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
                if reader:
                    images = convert_from_path(file_path)
                    for image in images:
                        # Preprocess each page image
                        processed_img = preprocess_image(image)
                        img_np = np.array(processed_img)
                        # Use paragraph=True to help join related text blocks (like digits)
                        result = reader.readtext(img_np, detail=0, paragraph=True)
                        # Mark OCR text with a special prefix for the extractor
                        text += "[OCR] " + " ".join(result) + " "
                else:
                    logger.error("EasyOCR reader not initialized")
        
        elif ext in ['png', 'jpg', 'jpeg']:
            if reader:
                # 1. Open and Preprocess for high accuracy OCR
                img = Image.open(file_path)
                processed_img = preprocess_image(img)
                
                # 2. Extract RAW text using EasyOCR
                img_np = np.array(processed_img)
                # Use paragraph=True to help join related text blocks
                result = reader.readtext(img_np, detail=0, paragraph=True)
                # Mark OCR text with a special prefix
                text = "[OCR] " + " ".join(result)
                
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
    Includes autocontrast for uneven lighting and optimized sharpening.
    """
    # 1. Resize for OCR (2200px width is sweet spot for EasyOCR)
    width, height = img.size
    target_width = 2200
    if width < target_width:
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
