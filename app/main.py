from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.report import router as report_router
from app.database import test_connection
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Grafana Webhook API",
    description="API untuk menerima alert dari Grafana dan menyimpan ke database",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    success, message = test_connection()
    if success:
        print(f"✓ {message}")
        print(f"✓ API Key loaded: {'Yes' if os.getenv('API_KEY') else 'NO - WARNING: API_KEY not set'}")
    else:
        print(f"✗ Database connection FAILED: {message}")
        print("  Pastikan MySQL XAMPP sudah running dan konfigurasi .env sudah benar")

app.include_router(report_router, prefix="/api")

@app.get("/")
def root():
    return {
        "status": "running",
        "app": "Grafana Webhook API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/report": "Terima alert dari Grafana",
            "GET /docs": "Swagger UI dokumentasi",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
def health_check():
    db_success, db_message = test_connection()
    return {
        "status": "ok" if db_success else "degraded",
        "database": {
            "connected": db_success,
            "message": db_message
        },
        "api_key_configured": bool(os.getenv("API_KEY"))
    }