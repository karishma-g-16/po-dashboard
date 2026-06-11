from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse, RedirectResponse
import io
from sqlalchemy.orm import Session
import os
import uuid
import logging
import pandas as pd

from backend.database.db import get_db
from backend.database.models import PurchaseOrder
from backend.app.auth import get_current_user

from backend.utils.storage import storage_manager
from backend.app.tasks import process_po_background

router = APIRouter(prefix="/api/po", tags=["po"])
logger = logging.getLogger(__name__)

# Ensure uploads folder exists (fallback)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/file/{po_id}")
async def get_po_file(
    po_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Serve the actual PO file (local or cloud)"""
    try:
        po_uuid = uuid.UUID(po_id)
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_uuid).first()
        
        if not po:
            raise HTTPException(status_code=404, detail="PO not found")
            
        # Try Supabase first
        public_url = storage_manager.get_public_url(po.file_path)
        if public_url:
            return RedirectResponse(public_url)
            
        # Fallback to local
        if not os.path.exists(po.file_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        return FileResponse(po.file_path)
    except Exception as e:
        logger.error(f"File serve error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{po_id}")
async def delete_po(
    po_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a PO - Restricted to specific admins"""
    try:
        # Authorization Check: Only this email can delete
        authorized_emails = ["karishmagautam178@gmail.com"]
        current_email = (current_user.get('email') or "").lower().strip()
        
        if current_email not in [email.lower() for email in authorized_emails]:
            return JSONResponse(
                status_code=403, 
                content={"success": False, "error": "Unauthorized. Only specific admins can delete data."}
            )

        po_uuid = uuid.UUID(po_id)
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_uuid).first()
        
        if not po:
            return JSONResponse(status_code=404, content={"success": False, "error": "PO not found"})
            
        # Delete from local if exists
        if os.path.exists(po.file_path):
            try:
                os.remove(po.file_path)
            except:
                pass
        
        # Note: Supabase deletion can be added here if needed
            
        db.delete(po)
        db.commit()
        
        return {"success": True, "message": "PO deleted successfully"}
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload invoice and trigger background processing"""
    
    try:
        if not file or not file.filename:
            return JSONResponse(status_code=400, content={"success": False, "error": "No file provided"})
        
        file_ext = file.filename.split('.')[-1].lower()
        allowed = ['pdf', 'xlsx', 'xls', 'csv', 'txt', 'png', 'jpg', 'jpeg']
        
        if file_ext not in allowed:
            return JSONResponse(status_code=400, content={"success": False, "error": f"File type not allowed."})
        
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}.{file_ext}"
        file_content = await file.read()
        
        # 1. Save to Cloud (Supabase) if configured
        storage_path = file_name
        success = await storage_manager.upload_content(file_content, file_name, file.content_type)
        
        # 2. Fallback to Local if cloud fails or not configured
        if not success:
            logger.warning("Cloud upload failed or skipped, saving locally.")
            local_path = os.path.join(UPLOAD_DIR, file_name)
            with open(local_path, "wb") as f:
                f.write(file_content)
            storage_path = local_path
        
        # 3. Create PO entry with PROCESSING status
        po = PurchaseOrder(
            id=uuid.UUID(file_id),
            user_id=current_user['id'],
            file_path=storage_path,
            file_type=file_ext,
            status='PROCESSING',
            uploaded_by=current_user['email'],
            company_name="Processing...",
            vendor_name="Pending...",
            total_amount=0,
            base_amount=0,
            gst_amount=0,
            four_percent_amount=0
        )
        
        db.add(po)
        db.commit()
        db.refresh(po)
        
        # 4. Trigger Background Processing
        background_tasks.add_task(process_po_background, str(po.id))
        
        return JSONResponse(
            status_code=202,
            content={
                "success": True,
                "po_id": str(po.id),
                "message": "File uploaded and processing started.",
                "status": "PROCESSING"
            }
        )
    
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": f"Upload failed: {str(e)}"})

@router.get("/export/csv")
async def export_csv(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export all POs to CSV (Public)"""
    try:
        pos = db.query(PurchaseOrder).all()
        
        data = []
        for po in pos:
            data.append({
                "Supplier": po.vendor_name,
                "Company": po.company_name,
                "Tracking": po.order_tracking,
                "Base Amount": float(po.base_amount),
                "GST (18%)": float(po.gst_amount),
                "4% Amount": float(po.four_percent_amount),
                "Total Amount": float(po.total_amount),
                "Credit Days": po.credit_days,
                "Status": po.status,
                "Uploaded At": po.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if po.uploaded_at else "N/A"
            })
            
        df = pd.DataFrame(data)
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        
        response = StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = "attachment; filename=purchase_orders.csv"
        return response
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/export/excel")
async def export_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export all POs to Excel (Public)"""
    try:
        pos = db.query(PurchaseOrder).all()
        
        data = []
        for po in pos:
            data.append({
                "Supplier": po.vendor_name,
                "Company": po.company_name,
                "Tracking": po.order_tracking,
                "Base Amount": float(po.base_amount),
                "GST (18%)": float(po.gst_amount),
                "4% Amount": float(po.four_percent_amount),
                "Total Amount": float(po.total_amount),
                "Credit Days": po.credit_days,
                "Status": po.status,
                "Uploaded At": po.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if po.uploaded_at else "N/A"
            })
            
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Purchase Orders')
            
        output.seek(0)
        
        response = StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response.headers["Content-Disposition"] = "attachment; filename=purchase_orders.xlsx"
        return response
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/list")
async def get_list(
    search: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all POs (Public)"""
    try:
        query = db.query(PurchaseOrder)
        
        if search:
            search_term = f"%{search}%"
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    PurchaseOrder.company_name.ilike(search_term),
                    PurchaseOrder.vendor_name.ilike(search_term),
                    PurchaseOrder.order_tracking.ilike(search_term)
                )
            )
            
        pos = query.order_by(PurchaseOrder.created_at.desc()).all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": str(po.id),
                    "company_name": po.company_name,
                    "vendor_name": po.vendor_name,
                    "total_amount": po.total_amount,
                    "base_amount": po.base_amount,
                    "gst_amount": po.gst_amount,
                    "four_percent_amount": po.four_percent_amount,
                    "credit_days": po.credit_days,
                    "order_tracking": po.order_tracking,
                    "ordered_quantity": po.ordered_quantity,
                    "status": po.status,
                    "uploaded_at": po.uploaded_at.isoformat() if po.uploaded_at else None
                }
                for po in pos
            ],
            "total": len(pos)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard stats (Public)"""
    try:
        pos = db.query(PurchaseOrder).all()
        
        total_amount = sum([p.total_amount for p in pos if p.total_amount]) or 0
        gst_total = sum([p.gst_amount for p in pos if p.gst_amount]) or 0
        
        return {
            "success": True,
            "total_invoices": len(pos),
            "total_amount": round(total_amount, 2),
            "gst_total": round(gst_total, 2),
            "pending_count": 0,
            "completed_count": len(pos)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
