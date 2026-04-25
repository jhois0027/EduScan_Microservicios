# services/procesamiento.py - VERSIÓN PRODUCCIÓN
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import base64
import logging
import asyncio
import time
from typing import List, Dict
from datetime import datetime
import os

# Importar validadores directamente (más confiable que HTTP)
from ia_validator import validar_calidad_imagen, procesar_imagen_examen

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EduScan Procesamiento")

# Configuración
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/jpg']
TIMEOUT_SEGUNDOS = 25

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "procesamiento",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/procesar")
async def procesar_imagen(file: UploadFile = File(...)):
    start_time = time.time()
    
    # 1. Validaciones básicas
    if file.size > MAX_IMAGE_SIZE:
        raise HTTPException(400, f"Imagen muy grande. Máx {MAX_IMAGE_SIZE//1024//1024}MB")
    
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"Formato no soportado. Usa JPEG o PNG")
    
    try:
        # 2. Leer imagen
        imagen_bytes = await file.read()
        
        # 3. Validar calidad (usando función local, no HTTP)
        valida, mensaje, confianza = validar_calidad_imagen(imagen_bytes)
        
        if not valida:
            return {
                "success": False,
                "error": mensaje,
                "recomendacion": "Toma una foto más nítida con buena iluminación",
                "tiempo_ms": (time.time() - start_time) * 1000
            }
        
        # 4. Procesar con Gemini (tu función ya existente)
        resultado = procesar_imagen_examen(imagen_bytes)
        
        # 5. Agregar metadata
        resultado["tiempo_procesamiento_ms"] = (time.time() - start_time) * 1000
        resultado["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Examen procesado - Nota: {resultado.get('nota')}, Tiempo: {resultado.get('tiempo_procesamiento_ms'):.0f}ms")
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Error interno del servidor",
                "detalle": str(e) if os.getenv("DEBUG") else None
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)