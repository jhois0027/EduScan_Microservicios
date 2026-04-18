# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import httpx
import os

app = FastAPI(title="EduScan Gateway", version="2.0")

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# URLS
# =========================
DATABASE_URL = os.getenv("DATABASE_URL", "https://eduscan-database.onrender.com")
IA_URL = os.getenv("IA_URL", "https://eduscan-ia.onrender.com")

# ⚠️ IMPORTANTE:
# Cambia esto según tu IA real
IA_ENDPOINT = "/corregir"  # ← AJUSTA SEGÚN /docs DE TU IA

# =========================
# PROXY
# =========================
async def forward_request(request: Request, target_url: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            if request.method == "GET":
                resp = await client.get(target_url, params=request.query_params)

            elif request.method == "POST":
                content_type = request.headers.get("content-type", "")

                if "multipart/form-data" in content_type:
                    form = await request.form()
                    files = {}
                    data = {}

                    for key, value in form.items():
                        if hasattr(value, "filename"):
                            files[key] = (
                                value.filename,
                                await value.read(),
                                value.content_type
                            )
                        else:
                            data[key] = value

                    resp = await client.post(target_url, data=data, files=files)

                else:
                    body = await request.body()
                    resp = await client.post(target_url, content=body)

            else:
                raise HTTPException(status_code=405, detail="Método no permitido")

            # 🔥 MANEJO DE ERRORES
            if resp.status_code != 200:
                return {
                    "error": "Error en microservicio",
                    "status": resp.status_code,
                    "detalle": resp.text
                }

            return resp.json()

        except Exception as e:
            return {"error": str(e)}

# =========================
# ENDPOINTS API
# =========================

@app.get("/api/alumnos")
async def get_alumnos(request: Request):
    return await forward_request(request, f"{DATABASE_URL}/alumnos")

@app.get("/api/examenes")
async def get_examenes(request: Request):
    return await forward_request(request, f"{DATABASE_URL}/examenes")

@app.post("/api/corregir-examen")
async def corregir(request: Request):
    return await forward_request(request, f"{IA_URL}{IA_ENDPOINT}")

@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# INTERFAZ CAMARA + SUBIDA
# =========================

@app.get("/camara", response_class=HTMLResponse)
async def camara():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>EduScan - Escanear Examen</title>
</head>

<body>

<h2>📸 Escanear o Subir Examen</h2>

<!-- CAMARA -->
<video id="video" autoplay playsinline style="width:300px; display:none;"></video>
<br>
<button onclick="abrirCamara()">Abrir Cámara</button>
<button onclick="tomarFoto()">Tomar Foto</button>

<br><br>

<!-- SUBIR -->
<input type="file" id="fileInput" accept="image/*">

<br><br>

<!-- PREVIEW -->
<img id="preview" style="width:300px; display:none;">
<canvas id="canvas" style="display:none;"></canvas>

<br><br>

<button onclick="enviar()">Enviar a IA</button>

<script>

let imagen = null;
let stream = null;

// CAMARA
async function abrirCamara() {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });

    const video = document.getElementById("video");
    video.srcObject = stream;
    video.style.display = "block";
}

function tomarFoto() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    canvas.getContext("2d").drawImage(video, 0, 0);

    imagen = canvas.toDataURL("image/jpeg");

    const img = document.getElementById("preview");
    img.src = imagen;
    img.style.display = "block";

    if (stream) stream.getTracks().forEach(t => t.stop());
}

// SUBIR IMAGEN
document.getElementById("fileInput").onchange = function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = function(ev) {
        imagen = ev.target.result;

        const img = document.getElementById("preview");
        img.src = imagen;
        img.style.display = "block";
    };

    reader.readAsDataURL(file);
};

// ENVIAR
async function enviar() {
    if (!imagen) {
        alert("Toma o sube una imagen primero");
        return;
    }

    const blob = await (await fetch(imagen)).blob();

    const form = new FormData();
    form.append("imagen", blob, "examen.jpg");

    const res = await fetch(window.location.origin + "/api/corregir-examen", {
        method: "POST",
        body: form
    });

    const data = await res.json();

    alert("Resultado: " + JSON.stringify(data));
}

</script>

</body>
</html>
"""

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))