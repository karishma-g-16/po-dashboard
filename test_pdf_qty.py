import os
import re
from backend.utils.document_processor import extract_text_from_file

uploads_dir = "uploads"
files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]

for f in files[:5]: # just check a few
    path = os.path.join(uploads_dir, f)
    print(f"\n--- Checking {f} ---")
    text = extract_text_from_file(path)
    
    # Check around Total
    idx = text.lower().rfind('total')
    if idx != -1:
        start = max(0, idx - 50)
        end = min(len(text), idx + 100)
        print("AROUND TOTAL:")
        print(repr(text[start:end]))
    
    # Check around Quantity / Qty
    match = re.search(r'(?i)quantity|qty|pcs', text)
    if match:
        idx = match.start()
        start = max(0, idx - 30)
        end = min(len(text), idx + 150)
        print("AROUND QUANTITY/QTY/PCS:")
        print(repr(text[start:end]))
