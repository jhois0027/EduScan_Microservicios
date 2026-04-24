import cv2
import numpy as np
import os
import re
import json
import base64
import google.generativeai as genai
from PIL import Image
import io

# --------------------------------
# VALIDADOR DE CALIDAD
# --------------------------------

def validar_calidad_imagen(imagen_bytes):
    try:
        nparr = np.frombuffer(imagen_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return False, "No se pudo leer la imagen", 0
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 80:
            return False, f"Imagen borrosa. Toma una foto más nítida.", laplacian_var
        
        if laplacian_var > 500:
            confianza = 0.9
        elif laplacian_var > 200:
            confianza = 0.8
        else:
            confianza = 0.6
            
        return True, "Calidad aceptable", round(confianza, 2)
        
    except Exception as e:
        return False, str(e), 0


# --------------------------------
# CORRECTOR CON GEMINI
# --------------------------------

def procesar_imagen_examen(imagen_bytes):
    """Corrige examen usando Gemini AI con análisis real"""
    
    print("📸 Procesando imagen...")
    
    # Validar calidad
    valida, mensaje, calidad = validar_calidad_imagen(imagen_bytes)
    
    if not valida:
        return {
            "success": False,
            "error": mensaje,
            "nota": 0,
            "confianza": calidad,
            "feedback": f"Calidad insuficiente: {mensaje}"
        }
    
    print(f"✅ Calidad aceptable (confianza: {calidad})")
    
    # Configurar Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY no configurada")
        return {
            "success": False,
            "error": "GEMINI_API_KEY no configurada en variables de entorno",
            "nota": 0,
            "confianza": 0,
            "feedback": "Error: API key no encontrada"
        }
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Preparar imagen
        image = Image.open(io.BytesIO(imagen_bytes))
        
        print("🤖 Enviando a Gemini para análisis...")
        
        # Prompt detallado para corrección precisa
        prompt = """
        Eres un corrector de exámenes profesional. Analiza DETALLADAMENTE la imagen del examen.

        ### INSTRUCCIONES:
        1. Lee TODAS las respuestas del estudiante
        2. Evalúa cada respuesta según su corrección
        3. Calcula la nota en escala de 0.0 a 5.0
        
        ### ESCALA DE NOTAS:
        - 5.0: Todas las respuestas son correctas y completas
        - 4.0 - 4.9: Mayoría de respuestas correctas, algunos errores menores
        - 3.0 - 3.9: Aproximadamente la mitad de las respuestas correctas
        - 1.0 - 2.9: Pocas respuestas correctas
        - 0.0: No respondió nada o todo incorrecto
        
        ### REGLAS ADICIONALES:
        - Si la respuesta es correcta pero tiene errores de ortografía, baja 0.1
        - Si la respuesta está incompleta, da la mitad del puntaje
        - Si no se entiende la respuesta, es incorrecta
        
        ### RESPUESTA (SOLO JSON, NADA MÁS):
        {
            "nota": 4.2,
            "preguntas_totales": 10,
            "respuestas_correctas": 8,
            "feedback": "Buen trabajo en la mayoría de preguntas. Revisar conceptos de...",
            "debilidades": ["tema que debe mejorar"],
            "fortalezas": ["tema que domina"],
            "confianza": 0.9
        }
        """
        
        response = model.generate_content([prompt, image])
        
        print("📥 Respuesta recibida de Gemini")
        
        # Extraer JSON
        texto = response.text
        print(f"Respuesta raw: {texto[:200]}...")
        
        json_match = re.search(r'\{[\s\S]*?\}', texto)
        
        if json_match:
            resultado = json.loads(json_match.group())
            nota = float(resultado.get('nota', 0))
            nota = max(0, min(5, nota))  # Limitar entre 0 y 5
            
            # Determinar estado según la nueva escala
            if nota < 3.6:
                estado_texto = "Reprueba"
                emoji = "❌"
            elif nota < 4.0:
                estado_texto = "Plan de mejoramiento"
                emoji = "⚠️"
            else:
                estado_texto = "Aprueba"
                emoji = "✅"
            
            feedback = resultado.get('feedback', f"{emoji} Nota: {nota} - {estado_texto}")
            
            # Agregar detalles de preguntas si existen
            preguntas_correctas = resultado.get('respuestas_correctas', 0)
            preguntas_totales = resultado.get('preguntas_totales', 10)
            
            porcentaje = (preguntas_correctas / preguntas_totales) * 100 if preguntas_totales > 0 else nota * 20
            
            return {
                "success": True,
                "nota": round(nota, 1),
                "nota_porcentaje": round(porcentaje, 1),
                "confianza": resultado.get('confianza', calidad),
                "feedback": feedback,
                "estado": estado_texto,
                "respuestas_correctas": preguntas_correctas,
                "preguntas_totales": preguntas_totales,
                "debilidades": resultado.get('debilidades', []),
                "fortalezas": resultado.get('fortalezas', []),
                "detalles_validacion": [
                    "✅ Imagen procesada correctamente",
                    f"🤖 IA confianza: {resultado.get('confianza', calidad)}",
                    f"📊 {preguntas_correctas}/{preguntas_totales} respuestas correctas"
                ]
            }
        else:
            print("❌ No se encontró JSON en la respuesta")
            return {
                "success": False,
                "error": "No se pudo interpretar la respuesta de la IA",
                "nota": 0,
                "confianza": 0,
                "feedback": "Error en el formato de respuesta"
            }
            
    except Exception as e:
        print(f"❌ Error en Gemini: {str(e)}")
        return {
            "success": False,
            "error": f"Error en IA: {str(e)}",
            "nota": 0,
            "confianza": 0,
            "feedback": f"Error técnico: {str(e)}"
        }