# PO Management Dashboard - Project Context

## Project Overview
An enterprise-grade B2B SaaS application for managing purchase orders. It automates data extraction from uploaded invoices (PDF, Images, Excel, CSV, TXT) and calculates precise financial figures. The application operates as a collaborative environment where all registered users share a global dashboard of data.

## Core Mandates & Logic

### 1. Financial Calculations (GST Engine)
All calculations are derived from the **Total Amount (Inclusive of 18% GST)**:
- **Base Amount**: `Total ÷ 1.18`
- **GST Amount**: `Total - Base Amount`
- **4% Amount**: `Base Amount × 0.04` (Extraction only, not an addition)
- **Database Storage**: All stored as `DECIMAL(12,2)`.

### 2. Tech Stack (Updated)
- **Backend**: FastAPI (Python) + SQLAlchemy ORM.
- **Frontend**: React (Vite) + Tailwind CSS + Lucide Icons.
- **Unified Processing**: Centralized extraction in `backend/utils/document_processor.py` handling all file types.
- **OCR Engine**: **EasyOCR** with advanced image preprocessing (2200px Resizing + Autocontrast + Sharpening) for high accuracy on screenshots and photos.
- **Database**: PostgreSQL.

### 3. OCR & Extraction Logic (High Precision)
- **Multi-Modal Validation**: Uses `AmountExtractor` to anchor numeric totals to extracted "Amount in Words" (e.g., Lakhs, Crore). This ensures million-scale numbers are prioritized over smaller table fragments.
- **Resilient Scoring**: Collects numeric candidates and ranks them based on keyword proximity (Total, Chargeable), currency symbols (₹, Rs), footer position, and Indian currency formatting.
- **Metadata Filtering**: Automatically disqualifies non-financial numbers like GSTINs, CINs, and zip codes during extraction.
- **Greedy OCR Joining**: Intelligently merges fragmented OCR digits (e.g., `23 , 77 , 700`) into single valid numbers while protecting clean digital PDF columns.
- **Smart Metadata**: Extracts cleaned Supplier and Company names, automatically stripping address noise (e.g., A-55, Sector 63) to ensure a professional dashboard view.

### 4. Key Features
- **Public Collaborative Dashboard**: All registered users can see and manage all purchase orders.
- **Data-to-PDF Export**: Generates professional PDF Vouchers from extracted application data using `jsPDF`.
- **Global Search**: Instant real-time filtering by Supplier, Company, or Tracking ID.
- **Document Viewer**: Professional modal for previewing uploaded PDFs and Images.

## How to Run the Application

### 1. Backend (FastAPI)
Always run backend commands from the **project root** directory (`po-dashboard`).

**PowerShell (Recommended):**
```powershell
# Activate Environment
.\backend\venv\Scripts\Activate.ps1

# Run Server
uvicorn backend.main:app --reload
```

**CMD:**
```cmd
# Activate Environment
backend\venv\Scripts\activate.bat

# Run Server
uvicorn backend.main:app --reload
```

*Note: Ensure PostgreSQL is running and the `podashboard` database exists.*

### 2. Frontend (React + Vite)
Open a separate terminal window.

```powershell
cd frontend
npm install
npm run dev
```

## Project Structure
- `backend/`: FastAPI application, models, routing, and shared extraction utilities (`utils/extraction.py`, `utils/amount_extractor.py`).
- `frontend/`: React SPA with functional components for Table, Upload, and Document Viewing.
- `uploads/`: Directory for storing original uploaded files.

## Workflow for New Features
1. **Extraction Logic**: Update `backend/utils/extraction.py` or `backend/utils/amount_extractor.py`.
2. **Backend API**: Add endpoints to `backend/app/routes.py`.
3. **Frontend API**: Add handlers to `frontend/src/api.js`.
4. **UI Components**: Update React files in `frontend/src/components/` or `frontend/src/pages/`.
  