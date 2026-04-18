from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(title="EduScan Gateway", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "https://eduscan-database.onrender.com")
IA_URL = os.getenv("IA_URL", "https://eduscan-ia.onrender.com")

# =========================
# FUNCION PROXY
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
                            files[key] = (value.filename, await value.read(), value.content_type)
                        else:
                            data[key] = value

                    resp = await client.post(target_url, data=data, files=files)
                else:
                    body = await request.body()
                    resp = await client.post(target_url, content=body)

            else:
                raise HTTPException(status_code=405, detail="Método no permitido")

            return resp.json()

        except Exception as e:
            return {"error": str(e)}

# =========================
# ENDPOINTS VISIBLES
# =========================

@app.get("/api/alumnos")
async def get_alumnos(request: Request):
    return await forward_request(request, f"{DATABASE_URL}/alumnos")

@app.get("/api/examenes")
async def get_examenes(request: Request):
    return await forward_request(request, f"{DATABASE_URL}/examenes")

@app.post("/api/corregir-examen")
async def corregir(request: Request):
    return await forward_request(request, f"{IA_URL}/corregir-examen")

@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))