def calculate_gst(gross_amount: float, gst_rate: float = 18.0) -> dict:
    """
    Calculate GST using EXACT formula
    
    Given: Gross Amount (with GST included)
    GST Rate: r% (default 18%)
    
    Formula:
    1. Actual Amount = Gross / (1 + r/100)
    2. GST Amount = Gross - Actual
    3. 4% Amount = Actual × 0.04
    
    Example:
    Gross = 11,800, r = 18
    Actual = 11,800 / 1.18 = 10,000
    GST = 11,800 - 10,000 = 1,800
    4% = 10,000 × 0.04 = 400
    """
    
    try:
        # Validation
        gross = float(gross_amount)
        r = float(gst_rate)
        
        if gross <= 0:
            return {
                'gross_amount': 0,
                'actual_amount': 0,
                'gst_amount': 0,
                'four_percent_amount': 0,
                'gst_rate': r
            }
        
        # Step 1: Remove GST using exact formula
        # Actual Amount = Gross / (1 + r/100)
        multiplier = 1 + (r / 100)
        actual_amount = round(gross / multiplier, 2)
        
        # Step 2: Calculate GST Amount
        # GST Amount = Gross - Actual
        gst_amount = round(gross - actual_amount, 2)
        
        # Step 3: Calculate 4% of Actual Amount
        # 4% Amount = Actual × 0.04
        four_percent_amount = round(actual_amount * 0.04, 2)
        
        # Verification
        # Verify: Actual + GST = Gross
        verify = round(actual_amount + gst_amount, 2)
        
        if verify != round(gross, 2):
            import logging
            logging.getLogger(__name__).warning(f"Calculation mismatch. {actual_amount} + {gst_amount} = {verify} (expected {gross})")
        
        return {
            'gross_amount': round(gross, 2),
            'actual_amount': actual_amount,
            'gst_amount': gst_amount,
            'four_percent_amount': four_percent_amount,
            'gst_rate': r
        }
    
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"GST Calculation Error: {e}")
        return {
            'gross_amount': 0,
            'actual_amount': 0,
            'gst_amount': 0,
            'four_percent_amount': 0,
            'gst_rate': 18.0
        }
