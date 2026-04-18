# eduscan-ia/app.py
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
import httpx
import json
from datetime import datetime

app = FastAPI(title="EduScan IA Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "TU_API_KEY_AQUI")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# ============================================
# CORRECCIÓN DE EXÁMENES CON GEMINI
# ============================================
@app.post("/corregir-examen")
async def corregir_examen(
    id_examen: int = Form(...),
    id_alumno: int = Form(...),
    imagen: UploadFile = File(...)
):
    try:
        # Leer imagen
        image_bytes = await imagen.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Obtener preguntas del examen desde la base de datos
        # (esto lo conectas con tu API de base de datos)
        preguntas = await obtener_preguntas(id_examen)
        
        if not preguntas:
            # Preguntas de ejemplo
            preguntas = [
                {"id": 1, "texto": "¿Cuánto es 2 + 2?", "respuesta_correcta": "4", "puntaje": 1},
                {"id": 2, "texto": "¿Cuánto es 5 x 3?", "respuesta_correcta": "15", "puntaje": 1},
                {"id": 3, "texto": "¿Cuál es la raíz cuadrada de 16?", "respuesta_correcta": "4", "puntaje": 1}
            ]
        
        # Extraer respuestas con Gemini
        respuestas_alumno = await extraer_respuestas_con_gemini(image_base64, preguntas)
        
        # Calcular puntaje
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
                "respuesta_esperada": pregunta["respuesta_correcta"],
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
            "mensaje": f"Examen corregido correctamente. Nota: {porcentaje}%"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def extraer_respuestas_con_gemini(image_base64: str, preguntas: list):
    """Envía la imagen a Gemini y extrae las respuestas"""
    
    # Construir prompt con las preguntas
    prompt = f"""Eres un profesor corrigiendo un examen.
    Estas son las preguntas del examen:
    {json.dumps(preguntas, ensure_ascii=False)}
    
    Analiza la imagen del examen y extrae SOLO las respuestas que escribió el alumno.
    Devuelve SOLO un JSON con este formato: {{"respuestas": ["respuesta1", "respuesta2", ...]}}
    Si una respuesta no es clara o no está visible, escribe "No respondida".
    No incluyas texto adicional fuera del JSON."""
    
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
        
        try:
            texto = data["candidates"][0]["content"]["parts"][0]["text"]
            # Extraer JSON del texto
            import re
            json_match = re.search(r'\{.*\}', texto, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result.get("respuestas", [])
        except:
            pass
        
        return []


async def obtener_preguntas(id_examen: int):
    """Obtiene preguntas desde la base de datos"""
    # Aquí conectas con tu API de base de datos
    # Por ahora, devolvemos preguntas de ejemplo
    return [
        {"id": 1, "texto": "¿Cuánto es 2 + 2?", "respuesta_correcta": "4", "puntaje": 1},
        {"id": 2, "texto": "¿Cuánto es 5 x 3?", "respuesta_correcta": "15", "puntaje": 1},
        {"id": 3, "texto": "¿Cuál es la raíz cuadrada de 16?", "respuesta_correcta": "4", "puntaje": 1}
    ]


@app.get("/health")
def health():
    return {"status": "healthy", "service": "eduscan-ia"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8002)))