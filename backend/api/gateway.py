from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import List

app = FastAPI(title="EduScan API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROCESAMIENTO_URL = "http://localhost:8001"
IA_URL = "http://localhost:8002"

class RespuestaCorreccion(BaseModel):
    respuestas_alumno: List[float]
    puntajes_preguntas: List[float]
    correctas: int
    incorrectas: int
    nota_final: float
    detalles: dict

@app.get("/")
async def root():
    return {"mensaje": "EduScan API - Corrector de Examenes", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway"}

@app.post("/corregir", response_model=RespuestaCorreccion)
async def corregir_examen(file: UploadFile = File(...)):
    try:
        imagen_bytes = await file.read()
        
        # 1. Llamar al servicio de procesamiento
        async with httpx.AsyncClient(timeout=30.0) as client:
            procesamiento_resp = await client.post(
                f"{PROCESAMIENTO_URL}/procesar",
                files={"file": (file.filename, imagen_bytes, file.content_type)}
            )
            if procesamiento_resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Error en procesamiento")
            
            datos_procesados = procesamiento_resp.json()
        
        # 2. Procesar cada pregunta con IA
        respuestas_puntos = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for pregunta_img in datos_procesados["preguntas"]:
                ia_resp = await client.post(
                    f"{IA_URL}/predecir",
                    json={"imagen_base64": pregunta_img}
                )
                if ia_resp.status_code == 200:
                    respuestas_puntos.append(ia_resp.json()["puntaje"])
                else:
                    respuestas_puntos.append(0.0)
        
        # 3. Calcular nota final
        total_preguntas = len(respuestas_puntos)
        nota_final = sum(respuestas_puntos)
        nota_final = min(nota_final, 5.0)
        
        # 4. Calcular aprobadas/reprobadas (>= 3.0 es aprobado)
        aprobadas = sum(1 for p in respuestas_puntos if p >= 3.0)
        reprobadas = total_preguntas - aprobadas
        
        return RespuestaCorreccion(
            respuestas_alumno=respuestas_puntos,
            puntajes_preguntas=respuestas_puntos,
            correctas=aprobadas,
            incorrectas=reprobadas,
            nota_final=round(nota_final, 1),
            detalles={
                "total_preguntas": total_preguntas,
                "valor_por_pregunta": round(5.0/total_preguntas, 2) if total_preguntas > 0 else 0,
                "porcentaje": round((nota_final / 5.0) * 100, 1)
            }
        )
        
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Servicio de procesamiento no disponible")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
