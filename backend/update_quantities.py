import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import PurchaseOrder
from backend.utils.document_processor import extract_text_from_file
from backend.utils.extraction import extract_smart_data

# Use localhost for local dev
DATABASE_URL = "postgresql://postgres:Test123@localhost:5432/podashboard"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_existing_quantities():
    db = SessionLocal()
    pos = db.query(PurchaseOrder).all()
    updated_count = 0
    
    for po in pos:
        if os.path.exists(po.file_path):
            print(f"Reprocessing PO: {po.id} (Current Qty: {po.ordered_quantity})")
            print(f"Reprocessing PO: {po.id}")
            text = extract_text_from_file(po.file_path)
            data = extract_smart_data(text)

            if data.get('ordered_quantity', 0) > 0:
                po.ordered_quantity = data['ordered_quantity']
                updated_count += 1
                print(f"  -> Extracted new quantity: {po.ordered_quantity}")
    if updated_count > 0:
        db.commit()
        print(f"\nSuccessfully updated {updated_count} purchase orders with their correct quantities.")
    else:
        print("\nNo purchase orders needed updating or quantities could not be found.")

    db.close()

if __name__ == "__main__":
    update_existing_quantities()
