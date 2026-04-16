"""
Archivo principal para Render - Importa el backend real
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la app desde backend/main.py
try:
    from backend.main import app
    print("✅ Backend importado correctamente")
except ImportError as e:
    print(f"❌ Error importando backend: {e}")
    # Fallback: crear una app simple
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    app = FastAPI(title="EduScan API Fallback")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        # Buscar frontend
        frontend_dir = "frontend"
        if os.path.exists(frontend_dir):
            for file in ["dashboard_mobile.html", "index.html"]:
                filepath = os.path.join(frontend_dir, file)
                if os.path.exists(filepath):
                    return FileResponse(filepath)
        return {"message": "EduScan API", "status": "ok", "frontend_exists": os.path.exists(frontend_dir)}
    
    @app.get("/health")
    async def health():
        return {"status": "ok", "mode": "fallback"}
    
    @app.get("/api/alumnos")
    async def get_alumnos():
        return {"alumnos": []}

# Servir archivos estáticos del frontend
if os.path.exists("frontend"):
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    print("✅ Frontend estático montado")
