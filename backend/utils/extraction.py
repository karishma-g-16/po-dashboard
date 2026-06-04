import re
import logging

logger = logging.getLogger(__name__)

def parse_numeric(s):
    """Clean OCR numeric string: remove currency, spaces, and handle separators."""
    if not s: return 0.0
    # Remove currency symbols and non-numeric chars except . and ,
    # Also remove common OCR noise
    s = re.sub(r'[₹Rs$€£\s]', '', s)
    
    # Handle cases like "1,234.56" vs "1234.56" vs "1.234,56"
    if ',' in s and '.' in s:
        if s.find(',') < s.find('.'): # 1,234.56
            s = s.replace(',', '')
        else: # 1.234,56
            s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        # Check if it looks like a decimal (e.g., 10,00) or thousand (1,000)
        parts = s.split(',')
        if len(parts[-1]) == 2: # Likely decimal
            s = s.replace(',', '.')
        else:
            s = s.replace(',', '')
    
    try:
        return float(s)
    except ValueError:
        return 0.0

def clean_entity_name(name: str) -> str:
    """Remove addresses and noise from company names."""
    if not name or name == "Not found":
        return name
    
    # Common address markers that signal the end of a company name
    address_markers = [
        r'\s[A-Z]-[0-9]+', # A-55, D-206
        r'\sPlot\sNo',
        r'\sSector',
        r'\sNoida',
        r'\sPhase',
        r'\s\d{6}',      # Zip codes
        r'\sRoad',
        r'\sStreet'
    ]
    
    cleaned = name.strip()
    for marker in address_markers:
        match = re.search(marker, cleaned, re.IGNORECASE)
        if match:
            cleaned = cleaned[:match.start()].strip()
            
    # Remove trailing noise like commas, dots, and trailing separators
    cleaned = re.sub(r'[,.\s:-]+$', '', cleaned)
    
    return cleaned

def extract_smart_data(text: str) -> dict:
    """
    Enhanced extraction logic to handle messy OCR text and identify entities.
    """
    # Pre-clean text: normalize spaces
    clean_text = re.sub(r'\s+', ' ', text)
    
    # 1. Company & Supplier Name Extraction
    company = "Not found"
    supplier = "Not found"
    
    # Check for hardcoded known companies first if they appear at the start of address blocks
    if re.search(r'Go IP Global Services', clean_text, re.IGNORECASE):
        company = "Go IP Global Services Pvt. Ltd."
    elif re.search(r'GO IP', clean_text, re.IGNORECASE):
        company = "Go IP Global Services Pvt. Ltd."
    else:
        # Company (Buyer)
        company_patterns = [
            r'(?:INVOICE TO|Bill To|Ship To|Customer|Buyer|Ship to|Invoice\s*[:\s]*To)[\s\(\):-]*?([A-Z][A-Za-z0-9\s&,.-]{3,})'
        ]
        for p in company_patterns:
            match = re.search(p, clean_text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                # Stop if we hit noise or address markers
                val = re.split(r'(?i)dated|invoice|voucher|mode|terms|consignee', val)[0].strip()
                if not any(x in val.lower() for x in ['invoice', 'bill to', 'ship to']):
                    company = clean_entity_name(val)
                    if len(company) > 3: break

    # Supplier (Seller)
    supplier_patterns = [
        r'(?:Supplier|Bill From|Vendor|Seller|INVOICE FROM|Bill from|Supplier\s*[:\s]*\(?Bill\s*from\)?)[\s\(\):-]*?([A-Z][A-Za-z0-9\s&,.-]{3,})',
        r'Supplier[\s\S]{1,30}?\)\s*([A-Z][A-Za-z0-9\s&,.-]{3,})',
        r'(?:Compliance International)[\s\(\):-]*?([A-Z0-9\s&,.-]*)'
    ]
    for p in supplier_patterns:
        match = re.search(p, clean_text, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            # Stop if we hit noise or next section markers
            val = re.split(r'(?i)consignee|ship to|gstin|state|sl\s*no', val)[0].strip()
            noise_words = ['supplier', 'bill from', 'invoice from', 'go ip', 'goip', 'global services']
            if not any(x in val.lower() for x in noise_words):
                supplier = clean_entity_name(val)
                if len(supplier) > 3: break
    
    # 2. OTHER FIELDS
    days = 0
    # Improved pattern for "Mode/Terms of Payment: 60 Days"
    match = re.search(r'(?:Credit|NET|Days|Terms|Payment)[\s\S]{0,30}?(?:Terms)?[:\s]*(\d+)\s*Days', clean_text, re.IGNORECASE)
    if not match:
        match = re.search(r'(?:Credit|NET|Days|Terms)[:\s]*(\d+)', clean_text, re.IGNORECASE)
    
    if match:
        days = int(match.group(1))
    
    tracking = "N/A"
    tracking_patterns = [
        r'(?:Voucher No\.|Reference No\.|Invoice|Bill|Inv|PO|Order)[#\s\.:\-]+([A-Z0-9\-/]+)',
        r'(?:No|Num)[#\s\.:\-]+([A-Z0-9\-/]+)'
    ]
    for p in tracking_patterns:
        match = re.search(p, clean_text, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if len(candidate) > 2:
                tracking = candidate
                break

    ordered_quantity = 0
    # 1. First Pass: Try to find numbers followed strictly by units
    qty_matches = re.finditer(r'\b([0-9]{1,3}(?:[,\s]?[0-9]{3})*)\s*(?:pcs|nos|qty|items|pce)\b', clean_text, re.IGNORECASE)
    
    qty_vals = []
    for match in qty_matches:
        val_str = re.sub(r'[\s,]', '', match.group(1))
        try:
            val = int(val_str)
            if val > 0: qty_vals.append(val)
        except ValueError:
            pass
            
    # 2. Aggressive Fallback: Look for the specific "Total X pcs" structure
    # This handles extreme OCR noise where spaces/characters separate the number from the unit
    if not qty_vals:
        logger.info("Applying aggressive fallback for ordered_quantity extraction")
        # Pattern looks for "Total", then any junk/numbers, then "pcs"
        fallback_match = re.search(r'Total[\s\S]{0,30}?([0-9][0-9\s,]*[0-9])[\s\S]{0,10}?(?:pcs|nos)', clean_text, re.IGNORECASE)
        if fallback_match:
            raw_num = fallback_match.group(1)
            clean_num = re.sub(r'[^0-9]', '', raw_num)
            try:
                if clean_num:
                    qty_vals.append(int(clean_num))
            except ValueError:
                pass

    # 3. Keyword-Based Extraction (For documents where units are missing)
    if not qty_vals:
        logger.info("Applying keyword-based fallback for ordered_quantity extraction")
        kw_matches = re.finditer(r'(?:Total Quantity|Ordered Quantity|Order Qty|Quantity|Qty)[\s:-]+([0-9]{1,3}(?:[,\s]?[0-9]{3})*)', clean_text, re.IGNORECASE)
        for match in kw_matches:
            clean_num = re.sub(r'[^0-9]', '', match.group(1))
            try:
                if clean_num:
                    qty_vals.append(int(clean_num))
            except ValueError:
                pass

    if qty_vals:
        # Prevent picking up GSTINs or huge artifact numbers
        valid_qtys = [q for q in qty_vals if q < 10000000]
        if valid_qtys:
            ordered_quantity = max(valid_qtys)

    return {
        'company_name': company,
        'vendor_name': supplier, # Keep key as vendor_name for DB compatibility but it contains supplier
        'credit_days': days,
        'order_tracking': tracking,
        'ordered_quantity': ordered_quantity
    }
