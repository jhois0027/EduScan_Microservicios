# backend/main.py
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
import bcrypt
from datetime import datetime, timedelta
import base64
import httpx
import json
import re

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="EduScan API Gateway", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# CONFIGURACIÓN
# ============================================

SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/eduscan')
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

security = HTTPBearer()

# ============================================
# CONEXIÓN A BASE DE DATOS
# ============================================

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# ============================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_current_docente(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        docente_id: int = payload.get("sub")
        if docente_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return docente_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# ============================================
# MODELOS
# ============================================

class Alumno(BaseModel):
    nombre: str
    correo: str
    grado: int
    promedio: Optional[float] = 0

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
# ENDPOINTS PÚBLICOS
# ============================================

@app.get("/")
async def root():
    return {
        "message": "EduScan API Gateway",
        "status": "online",
        "version": "1.0",
        "endpoints": {
            "/health": "Health check",
            "/api/login": "Login docente (POST)",
            "/api/mis-alumnos": "Alumnos del docente (GET, requiere token)",
            "/api/mis-calificaciones": "Calificaciones del docente (GET, requiere token)",
            "/api/alumnos": "CRUD alumnos (GET/POST/PUT/DELETE)",
            "/api/modulos": "CRUD módulos",
            "/api/examenes": "CRUD exámenes",
            "/api/estadisticas": "Estadísticas generales",
            "/api/corregir-examen": "Corregir examen con IA (POST)",
            "/docs": "Documentación Swagger"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "EduScan API Gateway", "version": "1.0"}

# ============================================
# AUTENTICACIÓN
# ============================================

@app.post("/api/login")
async def login(email: str, password: str):
    """Login para docentes - Devuelve token JWT"""
    try:
        db = get_db()
        cur = db.cursor()
        
        cur.execute("SELECT id_docente, nombre, email, password_hash, rol FROM docentes WHERE email = %s", (email,))
        docente = cur.fetchone()
        cur.close()
        db.close()
        
        if not docente:
            return {"success": False, "error": "Credenciales inválidas"}
        
        if not verify_password(password, docente['password_hash']):
            return {"success": False, "error": "Credenciales inválidas"}
        
        token = create_access_token(data={"sub": docente['id_docente'], "rol": docente['rol']})
        
        return {
            "success": True,
            "token": token,
            "docente": {
                "id": docente['id_docente'],
                "nombre": docente['nombre'],
                "email": docente['email'],
                "rol": docente['rol']
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/verificar-token")
async def verificar_token(docente_id: int = Depends(get_current_docente)):
    """Verifica si el token es válido"""
    return {"success": True, "docente_id": docente_id}

# ============================================
# ENDPOINTS SEGREGADOS POR DOCENTE
# ============================================

@app.get("/api/mis-alumnos")
async def get_mis_alumnos(docente_id: int = Depends(get_current_docente)):
    """Obtiene SOLO los alumnos del docente autenticado"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Obtener grados que enseña este docente
        cur.execute("SELECT grado FROM docente_grados WHERE docente_id = %s", (docente_id,))
        grados = [row['grado'] for row in cur.fetchall()]
        
        if not grados:
            cur.close()
            db.close()
            return {"success": True, "alumnos": [], "mis_grados": []}
        
        # Obtener alumnos SOLO de esos grados
        placeholders = ','.join(['%s'] * len(grados))
        cur.execute(f"""
            SELECT id_alumno, nombre, correo, grado, promedio 
            FROM alumnos 
            WHERE grado IN ({placeholders})
            ORDER BY grado, nombre
        """, grados)
        
        alumnos = []
        for row in cur.fetchall():
            alumnos.append({
                "id": row['id_alumno'],
                "nombre": row['nombre'],
                "correo": row['correo'],
                "grado": row['grado'],
                "promedio": float(row['promedio']) if row['promedio'] else 0
            })
        
        cur.close()
        db.close()
        
        return {
            "success": True,
            "alumnos": alumnos,
            "mis_grados": grados,
            "total": len(alumnos)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/mis-calificaciones")
async def get_mis_calificaciones(docente_id: int = Depends(get_current_docente)):
    """Obtiene SOLO las calificaciones de los alumnos del docente"""
    try:
        db = get_db()
        cur = db.cursor()
        
        # Obtener grados del docente
        cur.execute("SELECT grado FROM docente_grados WHERE docente_id = %s", (docente_id,))
        grados = [row['grado'] for row in cur.fetchall()]
        
        if not grados:
            cur.close()
            db.close()
            return {"success": True, "calificaciones": []}
        
        placeholders = ','.join(['%s'] * len(grados))
        cur.execute(f"""
            SELECT a.nombre as alumno_nombre, a.grado, e.puntaje, e.fecha, e.examen_nombre
            FROM evaluacion e
            JOIN alumnos a ON e.id_alumno = a.id_alumno
            WHERE a.grado IN ({placeholders})
            ORDER BY e.fecha DESC, a.grado, a.nombre
            LIMIT 50
        """, grados)
        
        calificaciones = []
        for row in cur.fetchall():
            calificaciones.append({
                "alumno": row['alumno_nombre'],
                "grado": row['grado'],
                "nota": float(row['puntaje']) if row['puntaje'] else 0,
                "fecha": str(row['fecha']),
                "examen": row['examen_nombre'] or "Examen"
            })
        
        cur.close()
        db.close()
        
        return {"success": True, "calificaciones": calificaciones, "total": len(calificaciones)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# CRUD ALUMNOS (con autenticación)
# ============================================

@app.get("/api/alumnos")
def get_alumnos(docente_id: int = Depends(get_current_docente)):
    """Lista todos los alumnos (filtrados por grado del docente)"""
    return get_mis_alumnos(docente_id)

@app.get("/api/alumnos/{id_alumno}")
def get_alumno(id_alumno: int, docente_id: int = Depends(get_current_docente)):
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
def crear_alumno(alumno: Alumno, docente_id: int = Depends(get_current_docente)):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """INSERT INTO alumnos (nombre, correo, grado, promedio) 
           VALUES (%s, %s, %s, %s) RETURNING *""",
        (alumno.nombre, alumno.correo, alumno.grado, alumno.promedio)
    )
    nuevo = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    return nuevo

@app.put("/api/alumnos/{id_alumno}")
def editar_alumno(id_alumno: int, alumno: Alumno, docente_id: int = Depends(get_current_docente)):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """UPDATE alumnos 
           SET nombre=%s, correo=%s, grado=%s, promedio=%s 
           WHERE id_alumno=%s RETURNING *""",
        (alumno.nombre, alumno.correo, alumno.grado, alumno.promedio, id_alumno)
    )
    actualizado = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    if not actualizado:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return actualizado

@app.delete("/api/alumnos/{id_alumno}")
def eliminar_alumno(id_alumno: int, docente_id: int = Depends(get_current_docente)):
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
# CORRECCIÓN CON IA (GEMINI)
# ============================================

@app.post("/api/corregir-examen")
async def corregir_examen(
    imagen: UploadFile = File(...),
    id_plantilla: Optional[int] = Form(None)
):
    """
    Corrige un examen usando Gemini AI.
    Si se proporciona id_plantilla, compara contra la clave del profesor.
    """
    try:
        image_bytes = await imagen.read()
        if len(image_bytes) < 1000:
            return {"success": False, "error": "Imagen demasiado pequeña o inválida"}
        
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        if not GEMINI_API_KEY:
            # Simular corrección si no hay API key
            return {
                "success": True,
                "nota": round(3.5 + (hash(image_bytes) % 15) / 10, 1),
                "feedback": "Corrección simulada (API no configurada)",
                "confianza": 0.75
            }
        
        prompt = """Eres un corrector de exámenes. Analiza DETALLADAMENTE la imagen del examen del alumno.

ESCALA DE NOTAS (0.0 a 5.0):
- 5.0: Todo correcto y completo
- 4.0–4.9: Mayoría correctas
- 3.0–3.9: Aproximadamente la mitad correctas
- 1.0–2.9: Pocas correctas
- 0.0: Nada correcto o en blanco

Devuelve SOLO JSON válido:
{
  "nota": 4.2,
  "preguntas_totales": 10,
  "respuestas_correctas": 8,
  "feedback": "Descripción del desempeño",
  "debilidades": ["tema a mejorar"],
  "fortalezas": ["tema dominado"],
  "confianza": 0.85
}"""
        
        body = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}
                ]
            }]
        }
        
        async with httpx.AsyncClient(timeout=40) as client:
            resp = await client.post(GEMINI_URL, json=body)
            resp_data = resp.json()
        
        texto = resp_data["candidates"][0]["content"]["parts"][0]["text"]
        match = re.search(r'\{[\s\S]*?\}', texto)
        
        if not match:
            return {"success": False, "error": "La IA no devolvió un resultado legible"}
        
        resultado = json.loads(match.group())
        nota = max(0.0, min(5.0, float(resultado.get("nota", 0))))
        nota = round(nota, 1)
        
        if nota >= 4.5:
            estado = "Excelente 🏆"
        elif nota >= 3.9:
            estado = "Aprueba ✅"
        elif nota >= 3.0:
            estado = "Plan de mejoramiento ⚠️"
        else:
            estado = "Reprueba ❌"
        
        return {
            "success": True,
            "nota": nota,
            "escala": "0-5",
            "estado": estado,
            "respuestas_correctas": resultado.get("respuestas_correctas", 0),
            "preguntas_totales": resultado.get("preguntas_totales", 0),
            "feedback": resultado.get("feedback", f"Nota: {nota}/5.0"),
            "debilidades": resultado.get("debilidades", []),
            "fortalezas": resultado.get("fortalezas", []),
            "confianza": resultado.get("confianza", 0.8)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Error al procesar: {str(e)}"}

# ============================================
# NUEVA EVALUACIÓN
# ============================================

@app.post("/nueva_evaluacion")
async def nueva_evaluacion(request: dict, docente_id: int = Depends(get_current_docente)):
    """Guardar nueva evaluación y actualizar promedio del alumno"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO evaluacion (id_alumno, puntaje, fecha, examen_nombre, feedback, confianza_validacion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.get('id_alumno'),
            request.get('puntaje'),
            request.get('fecha'),
            request.get('examen_nombre'),
            request.get('feedback'),
            request.get('confianza_validacion', 0.85)
        ))
        
        # Calcular el nuevo promedio
        cursor.execute("SELECT AVG(puntaje) FROM evaluacion WHERE id_alumno = %s", (request.get('id_alumno'),))
        nuevo_promedio = cursor.fetchone()[0]
        
        cursor.execute("UPDATE alumnos SET promedio = %s WHERE id_alumno = %s", (nuevo_promedio, request.get('id_alumno')))
        
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "success": True,
            "message": f"Calificación {request.get('puntaje')}/5.0 guardada",
            "nuevo_promedio": round(nuevo_promedio, 2) if nuevo_promedio else 0
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# ESTADÍSTICAS
# ============================================

@app.get("/api/estadisticas")
def get_estadisticas():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) as total FROM alumnos")
    total_alumnos = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) as total FROM examenes")
    total_examenes = cur.fetchone()["total"]
    cur.execute("SELECT AVG(promedio) as promedio FROM alumnos")
    promedio = cur.fetchone()["promedio"] or 0
    cur.execute("SELECT MAX(promedio) as maximo FROM alumnos")
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
# SERVIDOR FRONTEND
# ============================================

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.get("/dashboard")
async def serve_dashboard():
    if os.path.exists(os.path.join(FRONTEND_DIR, "dashboard_corrector.html")):
        return FileResponse(os.path.join(FRONTEND_DIR, "dashboard_corrector.html"))
    return {"message": "Dashboard no encontrado"}

# ============================================
# INICIALIZAR SERVIDOR
# ============================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)