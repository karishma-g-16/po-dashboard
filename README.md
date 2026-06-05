# PO Management Dashboard

A modern B2B SaaS dashboard for managing purchase orders with automated OCR extraction and GST calculations.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** React (Vite, TypeScript, Tailwind CSS)
- **Database:** PostgreSQL
- **Worker:** Celery + Redis
- **OCR:** Tesseract

## How to Run

### 1. Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Startup
Clone the repository and run:
```bash
docker-compose up --build
```

### 3. Access
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Features
- JWT Authentication
- Drag-and-drop Invoice Upload
- Automated Data Extraction (OCR)
- Precise GST Calculations
- Export to CSV/Excel
- Responsive Design (Light/Dark Mode)
"# po-dashboard" 
