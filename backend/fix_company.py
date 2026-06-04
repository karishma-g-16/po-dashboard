import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import PurchaseOrder

DATABASE_URL = "postgresql://postgres:Test123@localhost:5432/podashboard"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_company_names():
    db = SessionLocal()
    pos = db.query(PurchaseOrder).all()
    updated_count = 0
    
    for po in pos:
        if 'Go IP Global Services' in po.company_name or 'GO IP' in po.company_name or po.company_name == 'Pvt':
            print(f"Fixing PO {po.id}: Changing company name from '{po.company_name}' to 'Go IP Global Services Pvt. Ltd.'")
            po.company_name = 'Go IP Global Services Pvt. Ltd.'
            updated_count += 1
            
    if updated_count > 0:
        db.commit()
        print(f"\nSuccessfully updated {updated_count} purchase orders.")
    else:
        print("\nNo purchase orders needed updating.")

    db.close()

if __name__ == "__main__":
    fix_company_names()
