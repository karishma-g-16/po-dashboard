import re

texts = [
    "Total   15,000 pcs 12,09,500.00",
    "Total  10,000 pcs { 5,66,400.00",
    "Total  25,000 pcs 23,77,700.00"
]

for clean_text in texts:
    print(f"--- TEXT: {clean_text}")
    qty_matches = re.finditer(r'\b([0-9]{1,3}(?:[,\s]?[0-9]{3})*)\s*(?:pcs|nos|qty|items|pce)\b', clean_text, re.IGNORECASE)
    
    qty_vals = []
    for match in qty_matches:
        val_str = re.sub(r'[\s,]', '', match.group(1))
        try:
            val = int(val_str)
            if val > 0: qty_vals.append(val)
        except ValueError:
            pass
    print(f"Pass 1: {qty_vals}")
