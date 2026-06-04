import re

text = "PURCHASE ORDER Sok1 Invoice To cc Voucher No Daled Go IP Global Services Pvt: Ltd_ 8y^ NODIPO/2526/00970 9-Mar-26 D-206; Sector-63, Noida 201301"

clean_text = re.sub(r'\s+', ' ', text)
print("clean_text:", clean_text)

company_patterns = [
    r'(?:INVOICE TO|Bill To|Ship To|Customer|Buyer|Ship to|Invoice\s*[:\s]*To)[\s\(\):-]*?([A-Z][A-Za-z0-9\s&,.-]{3,})',
    r'(?:Go IP Global Services|GO IP)[\s\(\):-]*?([A-Z0-9\s&,.-]*)'
]

for p in company_patterns:
    match = re.search(p, clean_text, re.IGNORECASE)
    if match:
        print("Pattern match:", p)
        val = match.group(1).strip()
        print("Val raw:", val)
        val = re.split(r'(?i)dated|invoice|voucher|mode|terms|consignee', val)[0].strip()
        print("Val post-split:", val)

