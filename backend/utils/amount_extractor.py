import re
import logging

logger = logging.getLogger(__name__)

class AmountExtractor:
    
    @staticmethod
    def parse_numeric(s: str) -> float:
        """Clean OCR numeric string: handle all noise, corrupted symbols, and separators."""
        if not s: return 0.0
        # Aggressive cleaning for OCR: Remove everything except digits and dot
        # Example: "23 , 77 , 700 . 00" -> "2377700.00"
        s = re.sub(r'[^0-9\.]', '', s.replace(',', ''))
        
        if not s: return 0.0
        
        # Handle multiple dots (keep the last one)
        if s.count('.') > 1:
            parts = s.split('.')
            s = "".join(parts[:-1]) + "." + parts[-1]
        
        try:
            return float(s)
        except ValueError:
            return 0.0

    @staticmethod
    def find_total_amount(text: str) -> float:
        """
        High-Precision Extraction logic for both Digital PDFs and OCR images.
        """
        logger.info(f"--- STARTING EXTRACTION ---")
        logger.info(f"Input text length: {len(text)}")
        if len(text) < 100:
            logger.warning(f"EXTRACTED TEXT IS TOO SHORT: '{text}'")
        
        # Normalize text
        clean_text = text.replace('\ufffd', '₹').replace('?', '₹').replace('ī', '₹')
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Log first 500 chars of cleaned text for debugging
        logger.info(f"Cleaned Text Preview: {clean_text[:500]}...")
        
        # 1. Detect Magnitude from Words (e.g., "Two Lakhs...")
        words_mag = 0
        words_match = re.search(r'(?:Words|Chargeable|INR|Total)[\s\S]{0,250}?(?:Only)', clean_text, re.IGNORECASE)
        if words_match:
            wt = words_match.group(0).lower()
            if 'crore' in wt: words_mag = 10000000
            elif 'lakh' in wt: words_mag = 100000
            elif 'thousand' in wt: words_mag = 1000
            logger.info(f"Word Anchor Magnitude: {words_mag}")

        # 2. Identify Potential Candidates
        # Pattern designed to capture "₹ 23,77,700.00" or "2377700.00"
        pattern = r'(?:[₹Rs\?\$]\s*)?([0-9][0-9\s,\.]{1,25}[0-9])'
        matches = list(re.finditer(pattern, clean_text))
        
        candidates = []
        for match in matches:
            val_str = match.group(0).strip()
            # DISQUALIFY metadata: CINs (21 chars), GSTINs (15 chars), Phone numbers (10 digits)
            raw_digits = re.sub(r'[^0-9]', '', val_str)
            if len(raw_digits) >= 11 and '.' not in val_str: continue 
            if len(raw_digits) == 6 and '.' not in val_str: continue # Likely Zip

            val = AmountExtractor.parse_numeric(val_str)
            # Basic range check for a typical B2B PO
            if val < 50.0 or val > 99999999.0: continue
                
            score = 0
            
            # Decimal bonus
            if '.' in val_str and len(val_str.split('.')[-1]) == 2:
                score += 150
            
            # Word-Magnitude Bonus (Strongest indicator)
            if words_mag > 0:
                if val >= words_mag: score += 500
                elif val < words_mag / 20: score -= 300
                
            # Define context_before BEFORE logging it
            context_before = clean_text[max(0, match.start()-150):match.start()].upper()

            # Proximity to Total Keywords (Universal List)
            total_keywords = [
                'GRAND TOTAL', 'TOTAL AMOUNT', 'TOTAL', 'CHARGEABLE', 
                'NET PAYABLE', 'NET AMOUNT', 'FINAL AMOUNT', 'BALANCE DUE',
                'INVOICE TOTAL', 'VOUCHER TOTAL', 'AMOUNT PAYABLE'
            ]
            
            # Log the context for debugging
            logger.info(f"Candidate: {val} | Raw: '{val_str}' | Context: '{context_before[-50:]}'")
            
            for kw in total_keywords:
                if kw in context_before:
                    score += 300
                    if 'GRAND' in kw or 'INVOICE' in kw: score += 100
                    break
            
            # Currency symbol bonus (covers OCR artifacts like ī, ?, etc)
            if any(sym in val_str or sym in clean_text[max(0, match.start()-10):match.start()] for sym in ['₹', 'ī', 'Rs', 'INR', '$']):
                score += 200

            # Position in document: Totals are almost ALWAYS at the very end.
            # This is crucial for documents like PO-0044 where sub-totals exist.
            pos_ratio = match.start() / len(clean_text)
            if pos_ratio > 0.85: score += 300 # Heavy boost for bottom values
            elif pos_ratio > 0.7: score += 150
            candidates.append({'value': val, 'score': score, 'raw': val_str})

        if not candidates: return 0.0

        # Final Rank: Highest Score, then Highest Value
        candidates.sort(key=lambda x: (x['score'], x['value']), reverse=True)
        
        # Log top candidate for debugging
        top = candidates[0]
        logger.info(f"Top Candidate: {top['value']} (Score: {top['score']})")

        return round(top['value'], 2)
