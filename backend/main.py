# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="EduScan API", version="3.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# CONEXIÓN A BASE DE DATOS
# ============================================

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/eduscan')

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# ============================================
# MODELOS
# ============================================

class Alumno(BaseModel):
    nombre: str
    correo: str
    grado: int
    calificacion: Optional[float] = 0

class Modulo(BaseModel):
    nombre: str
    descripcion: Optional[str] = ""
    color: Optional[str] = "#3b82f6"
    grado: int

class Examen(BaseModel):
    nombre: str
    id_modulo: int
    grado: int
    fecha: str
    qr_code: Optional[str] = None

# ============================================
# ENDPOINTS - ALUMNOS
# ============================================

@app.get("/api/alumnos")
def get_alumnos():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM alumnos ORDER BY calificacion DESC")
    alumnos = cur.fetchall()
    cur.close()
    db.close()
    return {"alumnos": alumnos}

@app.get("/api/alumnos/{id_alumno}")
def get_alumno(id_alumno: int):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM alumnos WHERE id_alumno = %s", (id_alumno,))
    alumno = cur.fetchone()
    cur.close()
    db.close()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno

@app.post("/api/alumnos")
def crear_alumno(alumno: Alumno):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """INSERT INTO alumnos (nombre, correo, grado, calificacion) 
           VALUES (%s, %s, %s, %s) RETURNING *""",
        (alumno.nombre, alumno.correo, alumno.grado, alumno.calificacion)
    )
    nuevo = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    return nuevo

@app.put("/api/alumnos/{id_alumno}")
def editar_alumno(id_alumno: int, alumno: Alumno):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """UPDATE alumnos 
           SET nombre=%s, correo=%s, grado=%s, calificacion=%s 
           WHERE id_alumno=%s RETURNING *""",
        (alumno.nombre, alumno.correo, alumno.grado, alumno.calificacion, id_alumno)
    )
    actualizado = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    if not actualizado:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return actualizado

@app.delete("/api/alumnos/{id_alumno}")
def eliminar_alumno(id_alumno: int):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM alumnos WHERE id_alumno = %s RETURNING id_alumno", (id_alumno,))
    eliminado = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    if not eliminado:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return {"msg": "Alumno eliminado"}

# ============================================
# ENDPOINTS - MÓDULOS
# ============================================

@app.get("/api/modulos")
def get_modulos():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM modulos ORDER BY grado, nombre")
    modulos = cur.fetchall()
    cur.close()
    db.close()
    return {"modulos": modulos}

@app.post("/api/modulos")
def crear_modulo(modulo: Modulo):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """INSERT INTO modulos (nombre, descripcion, color, grado) 
           VALUES (%s, %s, %s, %s) RETURNING *""",
        (modulo.nombre, modulo.descripcion, modulo.color, modulo.grado)
    )
    nuevo = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    return nuevo

@app.put("/api/modulos/{id_modulo}")
def editar_modulo(id_modulo: int, modulo: Modulo):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """UPDATE modulos 
           SET nombre=%s, descripcion=%s, color=%s, grado=%s 
           WHERE id_modulo=%s RETURNING *""",
        (modulo.nombre, modulo.descripcion, modulo.color, modulo.grado, id_modulo)
    )
    actualizado = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    return actualizado

@app.delete("/api/modulos/{id_modulo}")
def eliminar_modulo(id_modulo: int):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM modulos WHERE id_modulo = %s RETURNING id_modulo", (id_modulo,))
    eliminado = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    return {"msg": "Módulo eliminado"}

# ============================================
# ENDPOINTS - EXÁMENES
# ============================================

@app.get("/api/examenes")
def get_examenes():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT e.*, m.nombre as modulo_nombre
        FROM examenes e
        JOIN modulos m ON e.id_modulo = m.id_modulo
        ORDER BY e.fecha DESC
    """)
    examenes = cur.fetchall()
    cur.close()
    db.close()
    return {"examenes": examenes}

@app.post("/api/examenes")
def crear_examen(examen: Examen):
    db = get_db()
    cur = db.cursor()
    qr_code = examen.qr_code or f"EXAM-{hash(examen.nombre) % 1000:03d}"
    cur.execute(
        """INSERT INTO examenes (nombre, id_modulo, grado, fecha, qr_code) 
           VALUES (%s, %s, %s, %s, %s) RETURNING *""",
        (examen.nombre, examen.id_modulo, examen.grado, examen.fecha, qr_code)
    )
    nuevo = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    return nuevo

@app.delete("/api/examenes/{id_examen}")
def eliminar_examen(id_examen: int):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM examenes WHERE id_examen = %s RETURNING id_examen", (id_examen,))
    eliminado = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    return {"msg": "Examen eliminado"}

# ============================================
# ENDPOINTS - ESTADÍSTICAS
# ============================================

@app.get("/api/estadisticas")
def get_estadisticas():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) as total FROM alumnos")
    total_alumnos = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) as total FROM examenes")
    total_examenes = cur.fetchone()["total"]
    cur.execute("SELECT AVG(calificacion) as promedio FROM alumnos")
    promedio = cur.fetchone()["promedio"] or 0
    cur.execute("SELECT MAX(calificacion) as maximo FROM alumnos")
    maximo = cur.fetchone()["maximo"] or 0
    cur.close()
    db.close()
    return {
        "total_alumnos": total_alumnos,
        "total_examenes": total_examenes,
        "promedio_general": round(float(promedio), 2),
        "mejor_nota": float(maximo)
    }

# ============================================
# SERVIR FRONTEND (ARCHIVOS HTML)
# IMPORTANTE: La carpeta frontend está en la raíz, no dentro de backend
# ============================================

# La ruta a la carpeta frontend (un nivel arriba de backend)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.get("/")
async def serve_frontend():
    """Servir el dashboard principal"""
    
    # Verificar si la carpeta frontend existe
    if not os.path.exists(FRONTEND_DIR):
        return {
            "message": "EduScan API funcionando",
            "status": "online",
            "error": f"No se encontró la carpeta frontend en: {FRONTEND_DIR}",
            "current_directory": os.getcwd(),
            "files": os.listdir(os.getcwd())
        }
    
    # Lista de posibles archivos a servir
    files_to_try = [
        "dashboard_mobile.html",
        "index.html",
        "dashboard_pc.html",
        "dashboard.html"
    ]
    
    for filename in files_to_try:
        filepath = os.path.join(FRONTEND_DIR, filename)
        if os.path.exists(filepath):
            return FileResponse(filepath)
    
    # Si no hay archivos HTML, mostrar lista de archivos disponibles
    return {
        "message": "No se encontró ningún archivo HTML",
        "frontend_files": os.listdir(FRONTEND_DIR),
        "suggested_endpoints": {
            "GET /api/alumnos": "Lista de alumnos",
            "GET /api/modulos": "Lista de módulos",
            "GET /api/examenes": "Lista de exámenes",
            "GET /api/estadisticas": "Estadísticas",
            "GET /docs": "Documentación Swagger"
        }
    }

# Servir archivos estáticos (CSS, JS, imágenes)
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "EduScan API", "version": "3.0"}

@app.get("/api")
def api_info():
    return {
        "message": "EduScan API",
        "endpoints": [
            "/api/alumnos",
            "/api/modulos", 
            "/api/examenes",
            "/api/estadisticas"
        ]
    }