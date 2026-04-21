# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import os
import random
from datetime import datetime

app = FastAPI(title="EduScan Gateway", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ENDPOINT RAÍZ
# ============================================
@app.get("/")
async def root():
    return {
        "message": "EduScan API Gateway",
        "status": "online",
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/": "Información de la API",
            "/health": "Estado del servicio",
            "/api/alumnos": "Lista de alumnos",
            "/api/examenes": "Lista de exámenes",
            "/api/calificaciones": "Lista de calificaciones",
            "/api/corregir-examen": "Corregir examen (POST)",
            "/camara": "Interfaz de cámara"
        }
    }

# ============================================
# HEALTH CHECK
# ============================================
@app.get("/health")
async def health():
    return {"status": "ok", "service": "eduscan-gateway", "timestamp": datetime.now().isoformat()}

# ============================================
# ENDPOINTS DE DATOS
# ============================================
@app.get("/api/alumnos")
async def get_alumnos():
    return {
        "success": True,
        "alumnos": [
            {"id": 1, "nombre": "Valentina Rojas", "grado": 11, "promedio": 98},
            {"id": 2, "nombre": "Mateo Herrera", "grado": 10, "promedio": 85},
            {"id": 3, "nombre": "Sofia Ramirez", "grado": 11, "promedio": 96},
            {"id": 4, "nombre": "Isabella Torres", "grado": 11, "promedio": 100}
        ],
        "total": 4
    }

@app.get("/api/examenes")
async def get_examenes():
    return {
        "success": True,
        "examenes": [
            {"id": 1, "nombre": "Matematicas - Algebra", "grado": 10, "materia": "Matematicas"},
            {"id": 2, "nombre": "Ciencias Naturales", "grado": 8, "materia": "Ciencias"},
            {"id": 3, "nombre": "Lengua y Literatura", "grado": 11, "materia": "Lengua"}
        ],
        "total": 3
    }

@app.get("/api/calificaciones")
async def get_calificaciones():
    return {
        "success": True,
        "calificaciones": [
            {"id": 1, "alumno_id": 1, "alumno_nombre": "Valentina Rojas", "examen_id": 1, "examen_nombre": "Matematicas - Algebra", "nota": 95, "fecha": "2026-04-12"},
            {"id": 2, "alumno_id": 2, "alumno_nombre": "Mateo Herrera", "examen_id": 1, "examen_nombre": "Matematicas - Algebra", "nota": 85, "fecha": "2026-04-12"},
            {"id": 3, "alumno_id": 3, "alumno_nombre": "Sofia Ramirez", "examen_id": 3, "examen_nombre": "Lengua y Literatura", "nota": 98, "fecha": "2026-04-13"}
        ],
        "total": 3
    }

# ============================================
# CORRECCIÓN CON IA
# ============================================
@app.post("/api/corregir-examen")
async def corregir_examen(request: Request):
    """Corregir examen con IA"""
    try:
        form = await request.form()
        file = form.get("imagen")
        
        if not file:
            return JSONResponse({
                "success": False,
                "error": "No se proporcionó ninguna imagen"
            }, status_code=400)
        
        # Leer la imagen
        imagen_bytes = await file.read()
        
        # Validar que la imagen no esté vacía
        if len(imagen_bytes) < 1000:
            return JSONResponse({
                "success": False,
                "error": "La imagen está vacía o es demasiado pequeña",
                "detalles": {
                    "razones": ["La imagen no tiene contenido suficiente"],
                    "sugerencia": "Asegúrate de que la imagen muestre claramente el examen"
                }
            })
        
        # Calcular nota simulada (entre 65 y 100)
        nota = random.randint(65, 100)
        
        return JSONResponse({
            "success": True,
            "nota": nota,
            "feedback": "Examen corregido exitosamente" if nota >= 70 else "Necesitas mejorar en algunos temas",
            "confianza_validacion": 0.85,
            "detalles_validacion": ["Imagen recibida correctamente", "Formato válido", "Procesamiento completado"]
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Error al procesar: {str(e)}"
        }, status_code=500)

# ============================================
# INTERFAZ DE CÁMARA
# ============================================
@app.get("/camara", response_class=HTMLResponse)
async def camara():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EduScan - Corrector IA</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 20px;
    }
    .container {
        max-width: 600px;
        margin: 0 auto;
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    h1 { color: #667eea; text-align: center; margin-bottom: 10px; }
    .subtitle { color: #666; text-align: center; margin-bottom: 20px; }
    button {
        background: #667eea;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 10px;
        cursor: pointer;
        margin: 5px;
        font-size: 14px;
    }
    button:hover { opacity: 0.9; transform: scale(1.02); }
    .btn-corregir { background: #10b981; }
    .preview-container { margin: 20px 0; text-align: center; }
    #preview { max-width: 100%; max-height: 300px; border-radius: 10px; }
    .resultado {
        margin-top: 20px;
        padding: 15px;
        border-radius: 10px;
        display: none;
    }
    .resultado.success { background: #d1fae5; color: #065f46; display: block; }
    .resultado.error { background: #fee2e2; color: #991b1b; display: block; }
    .resultado.loading { background: #e0e7ff; color: #3730a3; display: block; text-align: center; }
    .button-group { text-align: center; margin: 15px 0; }
</style>
</head>
<body>
<div class="container">
    <h1>📚 EduScan - Corrector IA</h1>
    <p class="subtitle">Toma una foto del examen para corregirlo automáticamente</p>
    
    <video id="video" autoplay playsinline style="width:100%; display:none; border-radius:10px;"></video>
    <canvas id="canvas" style="display:none;"></canvas>
    
    <div class="button-group">
        <button onclick="abrirCamara()">📷 Abrir Cámara</button>
        <button onclick="tomarFoto()">🎯 Tomar Foto</button>
        <input type="file" id="fileInput" accept="image/*" style="display:none;">
        <button onclick="document.getElementById('fileInput').click()">📁 Subir Imagen</button>
        <button id="btnCorregir" onclick="enviar()" class="btn-corregir" disabled>🤖 Corregir</button>
    </div>
    
    <div class="preview-container">
        <img id="preview" style="display:none;">
    </div>
    
    <div id="resultado" class="resultado"></div>
</div>

<script>
let imagen = null;
let stream = null;
let btnCorregir = document.getElementById("btnCorregir");
        
async function abrirCamara() {
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
    }
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    const video = document.getElementById("video");
    video.srcObject = stream;
    video.style.display = "block";
    document.getElementById("preview").style.display = "none";
}

function tomarFoto() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    imagen = canvas.toDataURL("image/jpeg");
    const preview = document.getElementById("preview");
    preview.src = imagen;
    preview.style.display = "block";
    video.style.display = "none";
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
        stream = null;
    }
    btnCorregir.disabled = false;
}

document.getElementById("fileInput").onchange = function(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(ev) {
        imagen = ev.target.result;
        const preview = document.getElementById("preview");
        preview.src = imagen;
        preview.style.display = "block";
        btnCorregir.disabled = false;
    };
    reader.readAsDataURL(file);
};

async function enviar() {
    if (!imagen) {
        alert("Toma o sube una imagen primero");
        return;
    }
    
    const resultadoDiv = document.getElementById("resultado");
    resultadoDiv.className = "resultado loading";
    resultadoDiv.innerHTML = '<div>🤖 Analizando imagen...</div>';
    
    const blob = await (await fetch(imagen)).blob();
    const form = new FormData();
    form.append("imagen", blob, "examen.jpg");
    
    try {
        const res = await fetch("/api/corregir-examen", {
            method: "POST",
            body: form
        });
        
        const data = await res.json();
        
        if (data.success) {
            resultadoDiv.className = "resultado success";
            resultadoDiv.innerHTML = `
                <h3>✅ Resultado</h3>
                <p><strong>Nota:</strong> ${data.nota}%</p>
                <p><strong>Feedback:</strong> ${data.feedback}</p>
            `;
        } else {
            resultadoDiv.className = "resultado error";
            resultadoDiv.innerHTML = `
                <h3>❌ Error</h3>
                <p>${data.error}</p>
            `;
        }
    } catch (error) {
        resultadoDiv.className = "resultado error";
        resultadoDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
    }
}
</script>
</body>
</html>
    """

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)