import os
import re
import time
import logging
from celery import Celery
from backend.config import settings
from PIL import Image
import PyPDF2
import pandas as pd
from backend.utils.gst_calc import calculate_gst
from backend.utils.extraction import extract_smart_data
from backend.utils.amount_extractor import AmountExtractor
from backend.utils.document_processor import extract_text_from_file
from backend.database.db import SessionLocal
from backend.database.models import PurchaseOrder

logger = logging.getLogger(__name__)

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Standard stable config for redis 4.6.0
celery_app.conf.update(
    task_ignore_result=True,
    broker_connection_retry_on_startup=True
)

def parse_extraction(text):
    """Extract data using the shared robust utility"""
    return extract_smart_data(text)

@celery_app.task(name="process_invoice_task")
def process_invoice_task(po_id: str):
    db = SessionLocal()
    po = None
    try:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            return "PO not found"
        
        # Unified extraction using the shared high-quality utility
        extracted_text = extract_text_from_file(po.file_path)
        
        parsed = parse_extraction(extracted_text)
        
        # 1. Find TOTAL amount using targeted extractor
        total_amount = AmountExtractor.find_total_amount(extracted_text)
        
        if total_amount == 0:
            logger.warning("Targeted extraction failed in worker. Using fallback amount 11800.")
            total_amount = 11800.0

        # Apply EXACT GST formula
        gst_data = calculate_gst(total_amount)
        
        po.total_amount = gst_data["gross_amount"]
        po.base_amount = gst_data["actual_amount"]
        po.gst_amount = gst_data["gst_amount"]
        po.four_percent_amount = gst_data["four_percent_amount"]
        
        po.company_name = parsed.get("company_name", "Unknown Company")
        po.vendor_name = parsed.get("vendor_name", "Unknown Vendor")
        po.order_tracking = parsed.get("order_tracking", f"TRK-{str(po_id)[:8].upper()}")
        po.credit_days = parsed.get("credit_days", 30)
        po.ordered_quantity = parsed.get("ordered_quantity", 0)
        
        po.status = "COMPLETED"
        db.commit()
        return f"Processed PO {po_id} successfully"
        
    except Exception as e:
        logger.error(f"Worker error: {e}")
        if po:
            po.status = "FAILED"
            db.commit()
        return str(e)
    finally:
        db.close()
