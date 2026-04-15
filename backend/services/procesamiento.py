from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
import base64

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "procesamiento"}

@app.post("/procesar")
async def procesar_imagen(file: UploadFile = File(...)):
    # Simular procesamiento de imagen
    # En producción aquí iría el código real con OpenCV
    
    # Crear 10 preguntas simuladas
    preguntas = []
    for i in range(10):
        # Crear imagen falsa en base64
        fake_img = np.zeros((64, 64), dtype=np.uint8)
        _, buffer = cv2.imencode('.png', fake_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        preguntas.append(img_base64)
    
    return {
        "preguntas": preguntas,
        "total_preguntas": 10,
        "dimensiones": [500, 700]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
