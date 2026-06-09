from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow absolute imports from the 'backend' package
# This is necessary for some deployment environments (like Render) that run from the backend folder.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database.db import engine, Base
from backend.app.routes import router as po_router
from backend.app.auth_routes import router as auth_router

load_dotenv()

app = FastAPI(
    title="PO Dashboard API",
    version="1.0.0"
)

# Create database tables on startup (non-blocking)
@app.on_event("startup")
async def startup_event():
    logging.info("FastAPI starting up...")
    # Run DB creation in a separate thread to avoid blocking the port binding
    import threading
    def init_db():
        logging.info("Background thread: Creating database tables...")
        try:
            Base.metadata.create_all(bind=engine)
            logging.info("Background thread: Database tables created successfully.")
        except Exception as e:
            logging.error(f"Background thread error: {e}")
    
    thread = threading.Thread(target=init_db)
    thread.start()
    logging.info("FastAPI ready and port binding should be complete.")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://*.vercel.app",
        "https://po-dashboard-frontend.vercel.app",
        "https://po-dashboard-frontend-gamma.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)

# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)

# Include routers
app.include_router(auth_router)
app.include_router(po_router)

@app.get("/")
def root():
    return {"message": "PO Dashboard API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
