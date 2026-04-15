import hashlib

class CorrectorIA:
    def __init__(self):
        self.opciones = ['A', 'B', 'C', 'D']
    
    def predecir(self, imagen_base64):
        hash_val = int(hashlib.md5(imagen_base64.encode()).hexdigest()[:8], 16)
        idx = hash_val % 4
        return {
            "respuesta": self.opciones[idx],
            "confianza": round(50 + (hash_val % 50), 2)
        }

corrector = CorrectorIA()