import cv2
import numpy as np


# --------------------------------
# Detector básico (placeholder)
# Reemplaza luego con OMR real
# --------------------------------

class DetectorRespuestas:

    def detectar_respuestas(self, imagen):
        """
        Simulación temporal.
        Luego aquí iría detección real de burbujas con OpenCV.
        Debe devolver algo como:
        ['A','C','B','D',...]
        """

        # SOLO ejemplo temporal:
        return [
            'A','B','C','D','A',
            'B','C','D','A','B'
        ]


# --------------------------------
# Validador básico
# --------------------------------

class ExamenValidator:

    def validar_imagen(self, imagen):

        if imagen is None:
            return {
                "es_examen": False,
                "error": "Imagen inválida"
            }

        alto, ancho = imagen.shape[:2]

        if alto < 300 or ancho < 300:
            return {
                "es_examen": False,
                "error": "Imagen demasiado pequeña"
            }

        return {
            "es_examen": True,
            "detalle": "Imagen válida"
        }


# --------------------------------
# Corrector principal
# --------------------------------

class CorrectorIA:

    def __init__(self):

        self.detector = DetectorRespuestas()
        self.validator = ExamenValidator()

        # Clave correcta ejemplo
        self.clave = [
            'A','B','C','D','A',
            'B','C','D','A','B'
        ]


    def corregir_examen(self, imagen):

        validacion = self.validator.validar_imagen(imagen)

        if not validacion["es_examen"]:
            return {
                "success": False,
                "error": "Imagen no válida",
                "detalles": validacion
            }

        respuestas_estudiante = (
            self.detector.detectar_respuestas(imagen)
        )


        # Validar respuestas completas
        if len(respuestas_estudiante) != len(self.clave):

            return {
                "success": False,
                "error": "Número de respuestas detectadas incompleto",
                "detectadas": len(respuestas_estudiante),
                "esperadas": len(self.clave)
            }


        aciertos = 0
        errores = []


        for i,(r,c) in enumerate(
            zip(respuestas_estudiante,self.clave),
            start=1
        ):

            if r == c:
                aciertos += 1

            else:
                errores.append({
                    "pregunta": i,
                    "marcada": r,
                    "correcta": c
                })


        # Nota en escala 0.0 a 5.0
        nota = round(
            (aciertos / len(self.clave)) * 5.0,
            2
        )


        return {

            "success": True,
            "nota": nota,
            "aciertos": aciertos,
            "total": len(self.clave),
            "errores": errores,
            "feedback": self._generar_feedback(nota)

        }


    def _generar_feedback(self, nota):

        if nota >= 4.6:
            return "Desempeño Superior"

        elif nota >= 4.0:
            return "Aprobado"

        elif nota >= 3.6:
            return "Plan de mejoramiento"

        else:
            return "Reprueba"



# --------------------------------
# Función integración para gateway
# --------------------------------

def procesar_imagen_examen(imagen_bytes):

    try:

        nparr = np.frombuffer(
            imagen_bytes,
            np.uint8
        )

        imagen = cv2.imdecode(
            nparr,
            cv2.IMREAD_COLOR
        )

        if imagen is None:

            return {
                "success": False,
                "error": "No se pudo leer imagen"
            }


        corrector = CorrectorIA()

        return corrector.corregir_examen(
            imagen
        )


    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }