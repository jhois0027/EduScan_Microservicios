from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import hashlib

app = FastAPI()

class PrediccionRequest(BaseModel):
    imagen_base64: str

class PrediccionResponse(BaseModel):
    puntaje: float
    confianza: float

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ia_modelo"}

@app.post("/predecir", response_model=PrediccionResponse)
async def predecir_respuesta(request: PrediccionRequest):
    try:
        # Usar hash de la imagen para generar puntaje determinista
        hash_val = int(hashlib.md5(request.imagen_base64.encode()).hexdigest()[:8], 16)
        # Puntaje entre 0.0 y 5.0
        puntaje = round((hash_val % 50) / 10.0, 1)
        puntaje = max(0.0, min(puntaje, 5.0))
        confianza = round(50 + (hash_val % 50), 2)
        
        return PrediccionResponse(puntaje=puntaje, confianza=confianza)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
