import os
import base64
import hashlib
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class PrediccionRequest(BaseModel):
    imagen_base64: str

class PrediccionResponse(BaseModel):
    puntaje: float
    confianza: float
    respuesta_detectada: str
    es_correcta: bool

def simular_puntaje_realista(imagen_base64):
    """Simulación que da puntajes VARIADOS (no siempre 2.5)"""
    # Usar hash de la imagen para generar puntaje determinista pero variado
    hash_val = int(hashlib.md5(imagen_base64.encode()).hexdigest()[:8], 16)
    
    # Distribución de puntajes:
    # 30% probabilidad de puntaje alto (4.0 - 5.0)
    # 40% probabilidad de puntaje medio (2.5 - 3.9)
    # 30% probabilidad de puntaje bajo (0.0 - 2.4)
    rand = hash_val % 100
    
    if rand < 30:  # Puntaje alto
        puntaje = round(4.0 + (hash_val % 10) / 10.0, 1)
    elif rand < 70:  # Puntaje medio
        puntaje = round(2.5 + (hash_val % 15) / 10.0, 1)
    else:  # Puntaje bajo
        puntaje = round((hash_val % 25) / 10.0, 1)
    
    puntaje = max(0.0, min(puntaje, 5.0))
    es_correcta = puntaje >= 3.0
    confianza = round(70 + (hash_val % 30), 2)
    
    return puntaje, confianza, es_correcta

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ia_modelo", "mode": "simulacion_variada"}

@app.post("/predecir", response_model=PrediccionResponse)
async def predecir_respuesta(request: PrediccionRequest):
    try:
        puntaje, confianza, es_correcta = simular_puntaje_realista(request.imagen_base64)
        
        return PrediccionResponse(
            puntaje=puntaje,
            confianza=confianza,
            respuesta_detectada="IA",
            es_correcta=es_correcta
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
