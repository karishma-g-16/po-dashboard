from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
import os
import uuid
import aiofiles
from backend.database.db import get_db
from backend.database.models import PurchaseOrder, User
from backend.app.schemas import PurchaseOrderResponse
from backend.config import settings
from backend.app.worker import process_invoice_task
from .auth_utils import get_current_user 

router = APIRouter()

@router.post("/po/upload", response_model=PurchaseOrderResponse)
async def upload_po(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Validation
    ext = file.filename.split(".")[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type .{ext} not supported")
    
    # 2. Path Management
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, file_name)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 3. NON-BLOCKING ASYNC SAVE
    # This keeps the API responsive even during large file writes
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024): # Read 1MB chunks
                await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Storage write failure")

    # 4. Fast DB Entry
    new_po = PurchaseOrder(
        id=file_id,
        user_id=current_user.id,
        file_path=file_path,
        file_type=file.content_type,
        uploaded_by=current_user.email,
        status="PROCESSING"
    )
    db.add(new_po)
    db.commit()
    db.refresh(new_po)
    
    # 5. FIRE-AND-FORGET CELERY TASK
    # We use countdown=1 to ensure DB is saved before worker looks for it
    try:
        process_invoice_task.apply_async(args=[str(new_po.id)], countdown=1)
    except Exception:
        # We don't fail the upload if Redis is briefly down, 
        # the dashboard will just show 'PROCESSING' until we fix Redis
        pass
    
    return new_po
