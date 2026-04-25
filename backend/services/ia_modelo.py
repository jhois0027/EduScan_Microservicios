import os
import base64
import io
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
import google.generativeai as genai

app = FastAPI()

class PrediccionRequest(BaseModel):
    imagen_base64: str

class PrediccionResponse(BaseModel):
    puntaje: float
    confianza: float
    respuesta_detectada: str
    es_correcta: bool
    feedback: str = ""

def obtener_estado_nota(nota):
    if nota >= 4.0:
        return "Aprueba"
    elif nota >= 3.5:
        return "Plan de mejoramiento"
    else:
        return "Reprueba"

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ia_modelo", "mode": "gemini"}

@app.post("/predecir")
async def predecir_respuesta(request: PrediccionRequest):
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            # Fallback a simulación si no hay API key
            return simular_respuesta(request.imagen_base64)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Decodificar imagen
        image_data = base64.b64decode(request.imagen_base64)
        image = Image.open(io.BytesIO(image_data))
        
        prompt = """
        Eres un corrector de exámenes. ESCALA: 0.0 a 5.0
        
        Reglas:
        - 5.0 = Excelente, todo correcto
        - 4.0 = Bueno, mayoría correcta
        - 3.5 = Plan de mejoramiento
        - 2.0 = Malo, pocas correctas
        - 0.0 = No respondió
        
        Responde SOLO JSON:
        {
            "puntaje": 4.2,
            "confianza": 0.9,
            "feedback": "Buen trabajo, mejorar en..."
        }
        """
        
        response = model.generate_content([prompt, image])
        
        import json
        import re
        texto = response.text
        json_match = re.search(r'\{[\s\S]*?\}', texto)
        
        if json_match:
            resultado = json.loads(json_match.group())
            puntaje = float(resultado.get('puntaje', 0))
            confianza = float(resultado.get('confianza', 0.7))
            feedback = resultado.get('feedback', '')
        else:
            puntaje, confianza, feedback = 2.5, 0.5, "Error en formato"
        
        puntaje = max(0.0, min(puntaje, 5.0))
        es_correcta = puntaje >= 3.5
        
        return PrediccionResponse(
            puntaje=round(puntaje, 1),
            confianza=round(confianza, 2),
            respuesta_detectada="IA",
            es_correcta=es_correcta,
            feedback=feedback
        )
        
    except Exception as e:
        # Fallback a simulación si hay error
        return simular_respuesta(request.imagen_base64)

def simular_respuesta(imagen_base64):
    import hashlib
    hash_val = int(hashlib.md5(imagen_base64.encode()).hexdigest()[:8], 16)
    rand = hash_val % 100
    
    if rand < 30:
        puntaje = round(4.0 + (hash_val % 10) / 10.0, 1)
        feedback = "Excelente trabajo"
    elif rand < 70:
        puntaje = round(2.5 + (hash_val % 15) / 10.0, 1)
        feedback = "Buen intento, revisa conceptos clave"
    else:
        puntaje = round((hash_val % 25) / 10.0, 1)
        feedback = "Necesitas mejorar, repasa los temas"
    
    return PrediccionResponse(
        puntaje=round(puntaje, 1),
        confianza=round(70 + (hash_val % 30), 2),
        respuesta_detectada="Simulación",
        es_correcta=puntaje >= 3.5,
        feedback=feedback
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)