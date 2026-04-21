"""
Servicio de validación de imágenes para detectar si realmente es un examen
"""
import cv2
import numpy as np
import re
from typing import Dict, Any, Tuple

class ExamenValidator:
    """Validador de imágenes de examen"""
    
    def __init__(self):
        self.confianza_minima = 0.6
        self.palabras_clave_examen = [
            'examen', 'prueba', 'evaluacion', 'test', 'quiz', 
            'pregunta', 'respuesta', 'nombre', 'fecha', 'grado',
            'materia', 'parcial', 'final', 'examination', 'test'
        ]
        
    def validar_imagen(self, imagen_cv2) -> Dict[str, Any]:
        """Valida si la imagen contiene un examen real"""
        resultados = {
            'es_examen': False,
            'confianza': 0.0,
            'razones': [],
            'texto_detectado': ''
        }
        
        # 1. Validar calidad de imagen
        calidad = self._validar_calidad_imagen(imagen_cv2)
        resultados['razones'].append(f"Calidad imagen: {calidad}")
        
        # 2. Detectar texto (simulado por ahora, mejor con OCR real)
        texto_detectado = self._simular_deteccion_texto(imagen_cv2)
        resultados['texto_detectado'] = texto_detectado
        
        # 3. Buscar palabras clave de examen
        palabras_encontradas = self._buscar_palabras_clave(texto_detectado)
        if palabras_encontradas:
            resultados['razones'].append(f"Palabras clave encontradas: {palabras_encontradas}")
            resultados['confianza'] += 0.3
        
        # 4. Validar estructura (preguntas, números, etc)
        tiene_preguntas = self._detectar_estructura_preguntas(texto_detectado)
        if tiene_preguntas:
            resultados['razones'].append("Estructura de preguntas detectada")
            resultados['confianza'] += 0.4
        
        # 5. Verificar que no sea una imagen genérica
        es_generica = self._detectar_imagen_generica(imagen_cv2)
        if not es_generica:
            resultados['confianza'] += 0.2
        
        # Determinar si es examen
        resultados['es_examen'] = resultados['confianza'] >= self.confianza_minima
        
        return resultados
    
    def _validar_calidad_imagen(self, imagen) -> str:
        """Valida la calidad de la imagen"""
        try:
            # Convertir a grises
            gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            
            # Calcular nitidez (varianza del Laplaciano)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if laplacian_var > 100:
                return "Buena calidad y nitidez"
            elif laplacian_var > 50:
                return "Calidad aceptable"
            else:
                return "Imagen borrosa - mejora el enfoque"
        except:
            return "No se pudo evaluar calidad"
    
    def _simular_deteccion_texto(self, imagen) -> str:
        """Simula detección de texto (reemplazar con OCR real como Tesseract)"""
        # Aquí iría Tesseract OCR real
        # Por ahora simulamos con datos de prueba
        textos_simulados = [
            "EXAMEN DE MATEMATICAS - Primer Parcial\nNombre: __________________\nFecha: __________________\n\nPregunta 1: 2 + 2 = ?\na) 3 b) 4 c) 5 d) 6\n\nPregunta 2: 5 x 3 = ?\na) 10 b) 12 c) 15 d) 20",
            "TEST DE CIENCIAS\nInstrucciones: Responde las siguientes preguntas\n1. Que es la fotosintesis?\n2. Menciona 3 tipos de energia",
            "EVALUACION DE HISTORIA\nTema: Independencia de Colombia\nPreguntas de seleccion multiple",
            "QUIZ DE INGLES\nVocabulary Test\n1. House means: a) Casa b) Carro c) Perro",
            "PRUEBA DE DIAGNOSTICO - GRADO 10\nNombre del estudiante: __________________"
        ]
        
        # Simular detección basada en características de la imagen
        import random
        return random.choice(textos_simulados) if random.random() > 0.3 else ""
    
    def _buscar_palabras_clave(self, texto: str) -> list:
        """Busca palabras clave de examen en el texto"""
        if not texto:
            return []
        
        texto_lower = texto.lower()
        encontradas = []
        
        for palabra in self.palabras_clave_examen:
            if palabra in texto_lower:
                encontradas.append(palabra)
        
        return encontradas
    
    def _detectar_estructura_preguntas(self, texto: str) -> bool:
        """Detecta si el texto tiene estructura de preguntas"""
        if not texto:
            return False
        
        patrones = [
            r'pregunta\s*\d+',
            r'\d+\.\s*\w+',
            r'[a-d]\)',
            r'[a-d]\.',
            r'verdadero|falso',
            r'seleccione|responda'
        ]
        
        for patron in patrones:
            if re.search(patron, texto.lower()):
                return True
        
        return False
    
    def _detectar_imagen_generica(self, imagen) -> bool:
        """Detecta si es una imagen genérica (no examen)"""
        try:
            # Verificar si la imagen es mayormente uniforme (fondo blanco, etc)
            gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            promedio = np.mean(gray)
            
            # Si es muy uniforme, podría ser una imagen sin contenido
            if promedio > 240 or promedio < 20:
                return True
            
            return False
        except:
            return False

class CorrectorIA:
    """Corrector de exámenes con validación"""
    
    def __init__(self):
        self.validator = ExamenValidator()
    
    def corregir_examen(self, imagen_cv2) -> Dict[str, Any]:
        """Corrige el examen solo si es válido"""
        
        # Primero validar la imagen
        validacion = self.validator.validar_imagen(imagen_cv2)
        
        if not validacion['es_examen']:
            return {
                'success': False,
                'error': 'No se detectó un examen válido en la imagen',
                'detalles': {
                    'confianza': validacion['confianza'],
                    'razones': validacion['razones'],
                    'sugerencia': 'Asegúrate de que la imagen muestre claramente un examen con preguntas y respuestas'
                }
            }
        
        # Si es válido, proceder con la corrección
        nota = self._calcular_nota(validacion['confianza'])
        
        return {
            'success': True,
            'nota': nota,
            'confianza_validacion': validacion['confianza'],
            'feedback': self._generar_feedback(nota),
            'detalles_validacion': validacion['razones'],
            'texto_detectado': validacion['texto_detectado'][:200]
        }
    
    def _calcular_nota(self, confianza_validacion: float) -> float:
        """Calcula nota basada en confianza y respuestas"""
        # Base de 60 puntos por ser examen válido
        nota_base = 60
        
        # Bonus por confianza de validación
        bonus_confianza = confianza_validacion * 20
        
        # Simular aciertos (esto iría con IA real)
        import random
        aciertos = random.randint(10, 20)
        nota_examen = (aciertos / 20) * 20
        
        nota_final = min(100, nota_base + bonus_confianza + nota_examen)
        
        return round(nota_final, 2)
    
    def _generar_feedback(self, nota: float) -> str:
        """Genera feedback según la nota"""
        if nota >= 90:
            return "Excelente! Dominas el tema."
        elif nota >= 70:
            return "Buen trabajo. Revisa algunos conceptos para mejorar."
        elif nota >= 60:
            return "Aprobado. Te recomiendo practicar más."
        else:
            return "No se pudo evaluar correctamente. Asegúrate de que el examen sea legible."

# Función principal para integrar con el gateway
def procesar_imagen_examen(imagen_bytes: bytes) -> Dict[str, Any]:
    """Procesa una imagen de examen y devuelve resultados"""
    try:
        # Convertir bytes a imagen OpenCV
        nparr = np.frombuffer(imagen_bytes, np.uint8)
        imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if imagen is None:
            return {
                'success': False,
                'error': 'No se pudo leer la imagen'
            }
        
        # Crear corrector y procesar
        corrector = CorrectorIA()
        resultado = corrector.corregir_examen(imagen)
        
        return resultado
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error procesando imagen: {str(e)}'
        }
