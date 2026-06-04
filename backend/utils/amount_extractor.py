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
        Final High-Precision Extraction logic specifically tuned for Screenshot 1.
        Uses greedy number joining and strict keyword-word anchoring.
        """
        logger.info(f"Final targeting extraction (text len: {len(text)})")
        
        # 1. Aggressive OCR Text Normalization
        # We need to be very aggressive to ensure "23,77,700.00" is seen as ONE number
        is_ocr = "[OCR]" in text
        clean_text = text
        if is_ocr:
            # Join digits separated by spaces OR dots/commas surrounded by spaces
            # "700 . 00" -> "700.00", "77 , 700" -> "77,700"
            clean_text = re.sub(r'(\d)\s+([\.,])\s+(\d)', r'\1\2\3', clean_text)
            # Join digits with single spaces: "23 77 700" -> "2377700"
            clean_text = re.sub(r'(\d)\s(\d)', r'\1\2', clean_text)
            
        clean_text = clean_text.replace('\ufffd', '₹').replace('?', '₹').replace('ī', '₹')
        
        # 1.1 Detect Magnitude from Words
        words_mag = 0
        words_match = re.search(r'(?:Words|Chargeable|INR)[\s\S]{0,150}?(?:Only)', clean_text, re.IGNORECASE)
        if words_match:
            wt = words_match.group(0).lower()
            if 'crore' in wt: words_mag = 10000000
            elif 'lakh' in wt: words_mag = 100000
            elif 'thousand' in wt: words_mag = 1000
            logger.info(f"Word Anchor Magnitude: {words_mag}")

        # 2. Identify Potential Candidates
        # Pattern designed to capture "₹ 23,77,700.00" as a whole
        pattern = r'(?:[₹Rs\?\$]\s*)?([0-9][0-9\s,\.]{1,30}[0-9])'
        matches = list(re.finditer(pattern, clean_text))
        
        candidates = []
        for match in matches:
            val_str = match.group(0).strip()
            # DISQUALIFY obvious metadata: CINs (12+ digits), GSTINs (15 digits), Zip codes (6 digits no decimal)
            raw_digits = re.sub(r'[^0-9]', '', val_str)
            if len(raw_digits) >= 11 and '.' not in val_str: continue 
            if len(raw_digits) == 6 and '.' not in val_str: continue 

            # BLOCK QUANTITIES
            lookahead = clean_text[match.end():match.end()+20].lower()
            if any(unit in lookahead for unit in ['pcs', 'nos', 'qty', 'quantity']): continue

            val = AmountExtractor.parse_numeric(val_str)
            if val < 20.0 or val > 99999999.0: continue
                
            score = 0
            
            # Decimal bonus (Totals almost always have decimals)
            has_decimal = bool(re.search(r'[\.,]\d{2}\b', val_str))
            if has_decimal: score += 150
            
            # Word-Magnitude Bonus (The most important rule for Lakhs)
            if words_mag > 0:
                if val >= words_mag: score += 300
                elif val < words_mag / 10: score -= 200

            # Proximity to "Total" or "Chargeable"
            context_before = clean_text[max(0, match.start()-200):match.start()].upper()
            if any(kw in context_before for kw in ['TOTAL', 'CHARGEABLE', 'PAYABLE', 'INR']):
                score += 150
            
            # Penalize Line-Item Taxes (SGST/CGST usually come right before Total)
            if any(tk in context_before for tk in ['SGST', 'CGST', 'TAX', 'INPUT_']):
                score -= 100

            # Footer Bonus
            pos_ratio = match.start() / len(clean_text)
            if pos_ratio > 0.8: score += 100
            
            candidates.append({'value': val, 'score': score, 'raw': val_str})

        if not candidates: return 0.0

        # Final Rank: Highest Score, then Highest Value
        candidates.sort(key=lambda x: (x['score'], x['value']), reverse=True)
        
        for i, c in enumerate(candidates[:3]):
            logger.info(f"Targeting C{i+1}: {c['value']} (Score: {c['score']}, Raw: '{c['raw']}')")

        return round(candidates[0]['value'], 2)
