from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
import httpx
import json
import random

app = FastAPI(title="EduScan IA Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

@app.post("/corregir-examen-simple")
async def corregir_examen_simple(
    id_alumno: int = Form(...),
    examen_nombre: str = Form(...),
    examen_grado: int = Form(...),
    imagen: UploadFile = File(...)
):
    try:
        image_bytes = await imagen.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        preguntas = [
            {"texto": "¿Cuánto es 2 + 2?", "respuesta_correcta": "4", "puntaje": 1},
            {"texto": "¿Cuánto es 5 x 3?", "respuesta_correcta": "15", "puntaje": 1},
            {"texto": "¿Cuál es la raíz cuadrada de 16?", "respuesta_correcta": "4", "puntaje": 1}
        ]
        
        respuestas_alumno = []
        
        if GEMINI_API_KEY:
            prompt = f"""Eres un profesor. Estas son las preguntas del examen:
{json.dumps(preguntas, ensure_ascii=False)}

Analiza la imagen y extrae SOLO las respuestas del alumno.
Devuelve SOLO JSON: {{"respuestas": ["respuesta1", "respuesta2", "respuesta3"]}}"""
            
            request_body = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}
                    ]
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(GEMINI_URL, json=request_body, timeout=30.0)
                data = response.json()
                texto = data["candidates"][0]["content"]["parts"][0]["text"]
                import re
                json_match = re.search(r'\{.*\}', texto, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    respuestas_alumno = result.get("respuestas", [])
        else:
            respuestas_alumno = ["4", "15", "4"]
        
        puntaje_total = 0
        puntaje_maximo = 0
        detalles = []
        
        for i, pregunta in enumerate(preguntas):
            respuesta_alumno = respuestas_alumno[i] if i < len(respuestas_alumno) else "No respondida"
            es_correcta = respuesta_alumno.lower().strip() == pregunta["respuesta_correcta"].lower().strip()
            puntaje_obtenido = pregunta["puntaje"] if es_correcta else 0
            
            puntaje_total += puntaje_obtenido
            puntaje_maximo += pregunta["puntaje"]
            
            detalles.append({
                "pregunta": pregunta["texto"],
                "respuesta_alumno": respuesta_alumno,
                "respuesta_correcta": pregunta["respuesta_correcta"],
                "puntaje_obtenido": puntaje_obtenido,
                "puntaje_maximo": pregunta["puntaje"],
                "correcta": es_correcta
            })
        
        porcentaje = round((puntaje_total / puntaje_maximo) * 100) if puntaje_maximo > 0 else 0
        
        return {
            "exito": True,
            "porcentaje": porcentaje,
            "puntaje_total": puntaje_total,
            "puntaje_maximo": puntaje_maximo,
            "respuestas": detalles,
            "alumno_nombre": f"Alumno {id_alumno}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy", "service": "eduscan-ia"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8002)))
