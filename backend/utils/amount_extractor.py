import re
import logging

logger = logging.getLogger(__name__)

class AmountExtractor:
    
    @staticmethod
    def parse_numeric(s: str) -> float:
        """Clean OCR numeric string: handle all noise, corrupted symbols, and separators."""
        if not s: return 0.0
        # Aggressive cleaning: Remove all spaces, currency symbols, and commas
        # Keep only digits and the LAST dot (decimal)
        s = re.sub(r'[^0-9\.]', '', s.replace(',', ''))
        
        if not s: return 0.0
        
        # Handle multiple dots (common OCR error)
        if s.count('.') > 1:
            # Keep only the last one as decimal
            parts = s.split('.')
            s = "".join(parts[:-1]) + "." + parts[-1]
        
        try:
            return float(s)
        except ValueError:
            return 0.0

    @staticmethod
    def find_total_amount(text: str) -> float:
        """
        Extremely resilient amount extraction using a candidate-scoring system.
        Supports International and Indian (Lakhs) numbering formats.
        """
        logger.info(f"Starting advanced amount extraction (text len: {len(text)})")
        
        is_ocr = "[OCR]" in text
        
        # 1. Pre-process text to handle common OCR artifacts
        # We only join digits with spaces IF it's OCR text, to avoid merging PDF columns
        clean_text = text
        if is_ocr:
            logger.info("OCR text detected, applying aggressive cleaning")
            # Only join if there's a single space between digits
            clean_text = re.sub(r'(\d)\s(\d)', r'\1\2', clean_text)
            
        # Handle spaces around separators (safe for both)
        clean_text = re.sub(r'(\d)\s*,\s*(\d)', r'\1,\2', clean_text)
        clean_text = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', clean_text)
        clean_text = clean_text.replace('\ufffd', '₹').replace('?', '₹').replace('ī', '₹')
        
        # Keywords for the total amount
        keywords = [
            'GRAND TOTAL', 'TOTAL AMOUNT', 'NET PAYABLE', 'BALANCE DUE', 
            'TOTAL PAYABLE', 'AMOUNT PAYABLE', 'INVOICE TOTAL', 'TOTAL',
            'NET AMOUNT', 'FINAL AMOUNT', 'AMOUNT DUE', 'PAYABLE', 'CHARGABLE'
        ]

        # 2. Identify all potential numeric candidates in the text
        # Regex explanation:
        # Match digits with commas, dots, or spaces as separators.
        # Supports: 1,234,567.00 (International) and 12,34,567.00 (Indian)
        # Also handles OCR artifacts like spaces within numbers.
        pattern = r'(?:[₹Rs\?\$]\s*)?([0-9][0-9\s,\.]{1,20}[0-9])'
        potential_matches = re.finditer(pattern, clean_text)
        
        candidates = []
        for match in potential_matches:
            val_str = match.group(0).strip()
            # Basic validation: must contain at least one digit
            if not any(c.isdigit() for c in val_str): continue
            
            val = AmountExtractor.parse_numeric(val_str)
            
            # Filter out obvious non-amounts (e.g., GSTINs, Phone numbers, Dates)
            # GSTINs are usually longer and don't have decimals. Phone numbers are 10 digits.
            if val < 10.0 or val > 50000000.0:
                continue
            
            raw_clean = re.sub(r'[^0-9]', '', val_str)
            if len(raw_clean) > 12: # Likely a GSTIN or random string of numbers
                continue
                
            # Basic Score
            score = 0
            
            # Feature: Has decimal point followed by 2 digits (Strong signal for currency)
            if re.search(r'[\.,]\d{2}\b', val_str):
                score += 35
                
            # Feature: Has currency symbol
            if any(sym in val_str for sym in ['₹', 'Rs', '$', 'ī']):
                score += 40

            # Feature: Proximity to keywords
            context_before = clean_text[max(0, match.start()-150):match.start()].upper()
            kw_found = False
            for kw in keywords:
                if kw in context_before:
                    dist = len(context_before) - context_before.rfind(kw)
                    if dist < 40:
                        score += 60
                    else:
                        score += 40
                    kw_found = True
                    break
            
            # Feature: Negative signal - is followed by units?
            lookahead = clean_text[match.end():match.end()+25].lower()
            if any(unit in lookahead for unit in ['pcs', 'nos', 'qty', 'quantity', 'items', 'pce', 'rate']):
                score -= 80 # Aggressively penalize quantities and rates
            
            # Feature: Position in document (Totals are almost always in the bottom 40%)
            pos_ratio = match.start() / len(clean_text)
            if pos_ratio > 0.6:
                score += 25
            if pos_ratio > 0.8:
                score += 15
            
            # Feature: Magnitude (Totals are often the largest valid number near keywords)
            # We add a small bonus for larger numbers to help resolve ties
            score += min(15, int(val / 10000))
            
            candidates.append({
                'value': val,
                'score': score,
                'pos': match.start(),
                'raw': val_str,
                'kw_found': kw_found
            })

        if not candidates:
            logger.warning("No amount candidates found")
            return 0.0

        # Sort by score DESC, then by value DESC
        candidates.sort(key=lambda x: (x['score'], x['value']), reverse=True)
        
        # Debug logging for top 5 candidates
        for i, c in enumerate(candidates[:5]):
            logger.info(f"Candidate {i+1}: {c['value']} (Score: {c['score']}, Raw: '{c['raw']}', KW: {c['kw_found']}, Pos: {c['pos']})")

        return round(candidates[0]['value'], 2)
