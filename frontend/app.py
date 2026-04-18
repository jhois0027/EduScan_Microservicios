from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import httpx
import os

app = FastAPI(title="EduScan API Gateway", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs de los servicios internos
DATABASE_URL = os.environ.get('DATABASE_URL', 'https://eduscan-database.onrender.com')
IA_URL = os.environ.get('IA_URL', 'https://eduscan-ia.onrender.com')

# ============================================
# P√ÅGINA PRINCIPAL PROFESIONAL
# ============================================
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EduScan API Gateway</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                min-height: 100vh;
                padding: 40px 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 50px;
            }
            .header h1 {
                font-size: 3rem;
                background: linear-gradient(135deg, #ffffff, #c7d2fe);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                margin-bottom: 10px;
            }
            .header p {
                color: #94a3b8;
                font-size: 1.1rem;
            }
            .badge {
                display: inline-block;
                background: rgba(99, 102, 241, 0.2);
                padding: 4px 12px;
                border-radius: 40px;
                font-size: 0.8rem;
                color: #a5b4fc;
                margin-top: 15px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 24px;
                margin-bottom: 40px;
            }
            .card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border-radius: 24px;
                padding: 24px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: transform 0.2s;
            }
            .card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.08);
            }
            .card h3 {
                color: white;
                font-size: 1.3rem;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .card h3 i {
                color: #8b5cf6;
            }
            .endpoint {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 12px;
                padding: 12px;
                margin-bottom: 10px;
            }
            .endpoint-method {
                display: inline-block;
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 0.7rem;
                font-weight: 600;
                margin-right: 10px;
            }
            .method-get { background: #10b981; color: white; }
            .method-post { background: #3b82f6; color: white; }
            .method-put { background: #f59e0b; color: white; }
            .method-delete { background: #ef4444; color: white; }
            .endpoint-url {
                color: #c7d2fe;
                font-family: monospace;
                font-size: 0.85rem;
                word-break: break-all;
            }
            .endpoint-desc {
                color: #94a3b8;
                font-size: 0.75rem;
                margin-top: 5px;
            }
            .services {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 24px;
                padding: 24px;
                margin-top: 20px;
            }
            .services h3 {
                color: white;
                margin-bottom: 16px;
            }
            .service-list {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
            }
            .service-item {
                background: rgba(99, 102, 241, 0.15);
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 0.85rem;
                color: #a5b4fc;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                color: #475569;
                font-size: 0.75rem;
            }
            @media (max-width: 768px) {
                .grid { grid-template-columns: 1fr; }
                .header h1 { font-size: 2rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Ì≥° EduScan API Gateway</h1>
                <p>Punto de entrada √∫nico para todos los servicios de EduScan</p>
                <div class="badge">
                    <i class="fas fa-code"></i> REST API ¬∑ <i class="fas fa-shield-alt"></i> CORS Enabled ¬∑ <i class="fas fa-chart-line"></i> v2.0.0
                </div>
            </div>

            <div class="grid">
                <!-- Alumnos -->
                <div class="card">
                    <h3><i class="fas fa-users"></i> Alumnos</h3>
                    <div class="endpoint">
                        <span class="endpoint-method method-get">GET</span>
                        <span class="endpoint-url">/alumnos</span>
                        <div class="endpoint-desc">Obtener todos los alumnos</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-get">GET</span>
                        <span class="endpoint-url">/alumnos/{id}</span>
                        <div class="endpoint-desc">Obtener un alumno por ID</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-post">POST</span>
                        <span class="endpoint-url">/alumnos</span>
                        <div class="endpoint-desc">Crear nuevo alumno</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-put">PUT</span>
                        <span class="endpoint-url">/alumnos/{id}</span>
                        <div class="endpoint-desc">Actualizar alumno</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-delete">DELETE</span>
                        <span class="endpoint-url">/alumnos/{id}</span>
                        <div class="endpoint-desc">Eliminar alumno</div>
                    </div>
                </div>

                <!-- Ex√°menes -->
                <div class="card">
                    <h3><i class="fas fa-file-alt"></i> Ex√°menes</h3>
                    <div class="endpoint">
                        <span class="endpoint-method method-get">GET</span>
                        <span class="endpoint-url">/examenes</span>
                        <div class="endpoint-desc">Obtener todos los ex√°menes</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-post">POST</span>
                        <span class="endpoint-url">/examenes</span>
                        <div class="endpoint-desc">Crear nuevo examen</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-put">PUT</span>
                        <span class="endpoint-url">/examenes/{id}</span>
                        <div class="endpoint-desc">Actualizar examen</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-delete">DELETE</span>
                        <span class="endpoint-url">/examenes/{id}</span>
                        <div class="endpoint-desc">Eliminar examen</div>
                    </div>
                </div>

                <!-- Calificaciones -->
                <div class="card">
                    <h3><i class="fas fa-star"></i> Calificaciones</h3>
                    <div class="endpoint">
                        <span class="endpoint-method method-get">GET</span>
                        <span class="endpoint-url">/calificaciones/alumno/{id}</span>
                        <div class="endpoint-desc">Obtener calificaciones de un alumno</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-post">POST</span>
                        <span class="endpoint-url">/calificaciones</span>
                        <div class="endpoint-desc">Guardar calificaci√≥n</div>
                    </div>
                </div>

                <!-- M√≥dulos -->
                <div class="card">
                    <h3><i class="fas fa-book"></i> M√≥dulos</h3>
                    <div class="endpoint">
                        <span class="endpoint-method method-get">GET</span>
                        <span class="endpoint-url">/modulos</span>
                        <div class="endpoint-desc">Obtener todos los m√≥dulos</div>
                    </div>
                </div>

                <!-- IA -->
                <div class="card">
                    <h3><i class="fas fa-robot"></i> Inteligencia Artificial</h3>
                    <div class="endpoint">
                        <span class="endpoint-method method-post">POST</span>
                        <span class="endpoint-url">/corregir-examen</span>
                        <div class="endpoint-desc">Corregir examen con IA (Gemini)</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-get">GET</span>
                        <span class="endpoint-url">/recomendaciones</span>
                        <div class="endpoint-desc">Recomendaciones para alumnos</div>
                    </div>
                </div>

                <!-- Sistema -->
                <div class="card">
                    <h3><i class="fas fa-cog"></i> Sistema</h3>
                    <div class="endpoint">
                        <span class="endpoint-method method-get">GET</span>
                        <span class="endpoint-url">/health</span>
                        <div class="endpoint-desc">Estado del servicio</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-get">GET</span>
                        <span class="endpoint-url">/docs</span>
                        <div class="endpoint-desc">Documentaci√≥n Swagger</div>
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method method-get">GET</span>
                        <span class="endpoint-url">/openapi.json</span>
                        <div class="endpoint-desc">Especificaci√≥n OpenAPI</div>
                    </div>
                </div>
            </div>

            <div class="services">
                <h3><i class="fas fa-network-wired"></i> Microservicios Conectados</h3>
                <div class="service-list">
                    <span class="service-item">Ì≥ä eduscan-database</span>
                    <span class="service-item">Ì∑† eduscan-ia</span>
                    <span class="service-item">‚öôÔ∏è eduscan-procesamiento</span>
                    <span class="service-item">Ì∑ÑÔ∏è EduScan_db (PostgreSQL)</span>
                    <span class="service-item">Ìæ® eduscan-dashboard</span>
                </div>
            </div>

            <div class="footer">
                <p>EduScan API Gateway v2.0.0 ¬∑ <i class="fas fa-lock"></i> CORS habilitado ¬∑ <i class="fas fa-tachometer-alt"></i> FastAPI</p>
            </div>
        </div>
    </body>
    </html>
    """

# ============================================
# HEALTH CHECK
# ============================================
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gateway", "version": "2.0.0"}

# ============================================
# PROXY A OTROS SERVICIOS
# ============================================
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    """Redirige las peticiones a los servicios correspondientes"""
    
    # Detectar servicio destino
    if path.startswith("alumnos") or path.startswith("examenes") or path.startswith("calificaciones") or path.startswith("modulos"):
        service_url = DATABASE_URL
    elif path.startswith("corregir") or path.startswith("recomendaciones"):
        service_url = IA_URL
    else:
        return {"error": "Ruta no encontrada", "path": path}
    
    target_url = f"{service_url}/{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            if request.method == "GET":
                resp = await client.get(target_url, params=request.query_params)
            elif request.method == "POST":
                body = await request.body()
                resp = await client.post(target_url, content=body, headers={"Content-Type": "application/json"})
            elif request.method == "PUT":
                body = await request.body()
                resp = await client.put(target_url, content=body, headers={"Content-Type": "application/json"})
            elif request.method == "DELETE":
                resp = await client.delete(target_url)
            else:
                return {"error": "M√©todo no soportado"}
            
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
