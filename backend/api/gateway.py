# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import random
from datetime import datetime, timedelta
import jwt
import bcrypt

app = FastAPI(title="EduScan Gateway", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas

security = HTTPBearer()


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
            "/api/login": "Login para docentes (POST)",
            "/api/mis-alumnos": "Lista de alumnos del docente (GET - requiere token)",
            "/api/mis-calificaciones": "Lista de calificaciones del docente (GET - requiere token)",
            "/api/alumnos": "Lista de alumnos (público - deprecated)",
            "/api/examenes": "Lista de exámenes",
            "/api/calificaciones": "Lista de calificaciones (público - deprecated)",
            "/api/corregir-examen": "Corregir examen (POST)",
            "/api/inicializar-bd": "Inicializar base de datos (GET)",
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
# AUTENTICACIÓN Y SEGREGACIÓN DE DOCENTES
# ============================================

@app.post("/api/login")
async def login(email: str, password: str):
    """Login para docentes - Devuelve token JWT"""
    import psycopg2
    
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            return {"success": False, "error": "DATABASE_URL no configurada"}
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_docente, nombre, email, password_hash, rol FROM docentes WHERE email = %s", (email,))
        docente = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not docente:
            return {"success": False, "error": "Credenciales inválidas"}
        
        if not verify_password(password, docente[3]):
            return {"success": False, "error": "Credenciales inválidas"}
        
        token = create_access_token(data={"sub": docente[0], "rol": docente[4]})
        
        return {
            "success": True,
            "token": token,
            "docente": {
                "id": docente[0],
                "nombre": docente[1],
                "email": docente[2],
                "rol": docente[4]
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/mis-alumnos")
async def get_mis_alumnos(docente_id: int = Depends(get_current_docente)):
    """Obtiene SOLO los alumnos del docente autenticado"""
    import psycopg2
    
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Obtener grados que enseña este docente
        cursor.execute("SELECT grado FROM docente_grados WHERE docente_id = %s", (docente_id,))
        grados = [row[0] for row in cursor.fetchall()]
        
        if not grados:
            cursor.close()
            conn.close()
            return {"success": True, "alumnos": [], "mis_grados": []}
        
        # Obtener alumnos SOLO de esos grados
        placeholders = ','.join(['%s'] * len(grados))
        cursor.execute(f"""
            SELECT id_alumno, nombre, correo, grado, promedio 
            FROM alumnos 
            WHERE grado IN ({placeholders})
            ORDER BY grado, nombre
        """, grados)
        
        alumnos = []
        for row in cursor.fetchall():
            alumnos.append({
                "id": row[0],
                "nombre": row[1],
                "correo": row[2],
                "grado": row[3],
                "promedio": float(row[4]) if row[4] else 0
            })
        
        cursor.close()
        conn.close()
        
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
    import psycopg2
    
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Obtener grados del docente
        cursor.execute("SELECT grado FROM docente_grados WHERE docente_id = %s", (docente_id,))
        grados = [row[0] for row in cursor.fetchall()]
        
        if not grados:
            cursor.close()
            conn.close()
            return {"success": True, "calificaciones": []}
        
        placeholders = ','.join(['%s'] * len(grados))
        cursor.execute(f"""
            SELECT a.nombre as alumno_nombre, a.grado, e.puntaje, e.fecha, e.examen_nombre
            FROM evaluacion e
            JOIN alumnos a ON e.id_alumno = a.id_alumno
            WHERE a.grado IN ({placeholders})
            ORDER BY e.fecha DESC, a.grado, a.nombre
            LIMIT 50
        """, grados)
        
        calificaciones = []
        for row in cursor.fetchall():
            calificaciones.append({
                "alumno": row[0],
                "grado": row[1],
                "nota": float(row[2]) if row[2] else 0,
                "fecha": str(row[3]),
                "examen": row[4] or "Examen"
            })
        
        cursor.close()
        conn.close()
        
        return {"success": True, "calificaciones": calificaciones, "total": len(calificaciones)}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/verificar-token")
async def verificar_token(docente_id: int = Depends(get_current_docente)):
    """Verifica si el token es válido"""
    return {"success": True, "docente_id": docente_id}

# ============================================
# ENDPOINTS DE DATOS (PÚBLICOS - DEPRECATED)
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

from services.ia_validator import procesar_imagen_examen

@app.post("/api/corregir-examen")
async def corregir_examen(request: Request):
    try:
        form = await request.form()
        file = form.get("imagen")

        if not file:
            return JSONResponse(
                {
                    "success": False,
                    "error": "No se proporcionó ninguna imagen"
                },
                status_code=400
            )

        imagen_bytes = await file.read()

        if len(imagen_bytes) < 1000:
            return JSONResponse(
                {
                    "success": False,
                    "error": "Imagen demasiado pequeña",
                    "detalles": {
                        "sugerencia": "Toma una foto donde se vea completo el examen"
                    }
                },
                status_code=400
            )

        # Aquí llama tu IA validator real
        resultado = procesar_imagen_examen(imagen_bytes)

        return JSONResponse(resultado)

    except Exception as e:
        return JSONResponse(
            {
                "success": False,
                "error": f"Error al procesar: {str(e)}"
            },
            status_code=500
        )

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
# INICIALIZAR BASE DE DATOS (DOCENTES)
# ============================================
@app.get("/api/inicializar-bd")
async def inicializar_base_datos():
    """
    Endpoint para inicializar las tablas de docentes en la base de datos.
    Llama a esta URL una vez para crear las tablas necesarias.
    
    Credenciales que se crearán:
    - ana@eduscan.com / password123 (ve grados 10° y 11°)
    - carlos@eduscan.com / password123 (ve grados 8° y 9°)
    - admin@eduscan.com / password123 (ve todo)
    """
    import psycopg2
    
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        if not DATABASE_URL:
            return {
                "success": False,
                "error": "DATABASE_URL no está configurada en las variables de entorno",
                "solucion": "Agrega DATABASE_URL en Environment Variables en Render"
            }
        
        print(f"Conectando a base de datos...")
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Crear tabla docentes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS docentes (
                id_docente SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(50) DEFAULT 'docente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla docente_grados
        cur.execute("""
            CREATE TABLE IF NOT EXISTS docente_grados (
                id SERIAL PRIMARY KEY,
                docente_id INTEGER REFERENCES docentes(id_docente) ON DELETE CASCADE,
                grado INTEGER NOT NULL,
                UNIQUE(docente_id, grado)
            )
        """)
        
        # Verificar si ya hay docentes
        cur.execute("SELECT COUNT(*) FROM docentes")
        count = cur.fetchone()[0]
        
        resultados = {
            "tablas_creadas": True,
            "docentes_existentes": count,
            "docentes_insertados": 0,
            "grados_asignados": 0
        }
        
        if count == 0:
            # Hash de contraseña 'password123'
            hash_pass = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtXEyMqCqB7QK'
            
            # Insertar docentes
            cur.execute("""
                INSERT INTO docentes (nombre, email, password_hash, rol) VALUES
                ('Prof. Ana Lopez', 'ana@eduscan.com', %s, 'docente'),
                ('Prof. Carlos Ruiz', 'carlos@eduscan.com', %s, 'docente'),
                ('Administrador', 'admin@eduscan.com', %s, 'admin')
                ON CONFLICT (email) DO NOTHING
                RETURNING id_docente, email
            """, (hash_pass, hash_pass, hash_pass))
            
            resultados["docentes_insertados"] = 3
            
            # Obtener IDs
            cur.execute("SELECT id_docente FROM docentes WHERE email = 'ana@eduscan.com'")
            ana = cur.fetchone()
            cur.execute("SELECT id_docente FROM docentes WHERE email = 'carlos@eduscan.com'")
            carlos = cur.fetchone()
            
            if ana and carlos:
                cur.execute("""
                    INSERT INTO docente_grados (docente_id, grado) VALUES
                    (%s, 10), (%s, 11), (%s, 8), (%s, 9)
                    ON CONFLICT (docente_id, grado) DO NOTHING
                """, (ana[0], ana[0], carlos[0], carlos[0]))
                resultados["grados_asignados"] = 4
        
        # Obtener lista de docentes para mostrar
        cur.execute("SELECT id_docente, nombre, email, rol FROM docentes")
        docentes = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Base de datos inicializada correctamente" if count == 0 else "Las tablas ya existían",
            "resultados": resultados,
            "docentes": [
                {"id": d[0], "nombre": d[1], "email": d[2], "rol": d[3]} 
                for d in docentes
            ],
            "credenciales": {
                "ana@eduscan.com": "password123 (grados 10° y 11°)",
                "carlos@eduscan.com": "password123 (grados 8° y 9°)",
                "admin@eduscan.com": "password123 (todos los grados)"
            }
        }
        
    except psycopg2.OperationalError as e:
        return {
            "success": False,
            "error": f"Error de conexión a la base de datos: {str(e)}",
            "solucion": "Verifica que DATABASE_URL esté correctamente configurada en las variables de entorno de Render"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        }

# ============================================
# NUEVA EVALUACIÓN
# ============================================
@app.post("/nueva_evaluacion")
async def nueva_evaluacion(request: Request):
    """Guardar nueva evaluación en la base de datos"""
    import psycopg2
    
    try:
        data = await request.json()
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        if not DATABASE_URL:
            return {"success": False, "error": "DATABASE_URL no configurada"}
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO evaluacion (id_alumno, puntaje, fecha, examen_nombre, feedback, confianza_validacion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data.get('id_alumno'),
            data.get('puntaje'),
            data.get('fecha'),
            data.get('examen_nombre'),
            data.get('feedback'),
            data.get('confianza_validacion', 0.85)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# CAMBIAR CONTRASEÑA (CONTRASEÑA CORTA)
# ============================================
@app.get("/api/cambiar-pass/{email}/{nueva_password}")
async def cambiar_password(email: str, nueva_password: str):
    """Cambia la contraseña de un docente a una más corta"""
    import psycopg2
    import bcrypt
    
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        if not DATABASE_URL:
            return {"success": False, "error": "DATABASE_URL no configurada"}
        
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cur = conn.cursor()
        
        # Generar hash de la nueva contraseña
        hashed = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cur.execute("UPDATE docentes SET password_hash = %s WHERE email = %s", (hashed, email))
        
        cur.close()
        conn.close()
        
        return {
            "success": True, 
            "message": f"Contraseña para {email} cambiada a '{nueva_password}'"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
       
# ============================================
# AGREGAR COLUMNAS A LA TABLA ALUMNOS
# ============================================
@app.get("/api/agregar-columnas")
async def agregar_columnas():
    import psycopg2
    
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cur = conn.cursor()
        
        # Agregar columnas faltantes
        cur.execute("ALTER TABLE alumnos ADD COLUMN IF NOT EXISTS correo VARCHAR(100)")
        cur.execute("ALTER TABLE alumnos ADD COLUMN IF NOT EXISTS grado INTEGER")
        cur.execute("ALTER TABLE alumnos ADD COLUMN IF NOT EXISTS promedio DECIMAL(5,2) DEFAULT 0")
        
        cur.close()
        conn.close()
        
        return {"success": True, "message": "Columnas agregadas correctamente: correo, grado, promedio"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    
  # ============================================
# INSERTAR ALUMNOS DE PRUEBA POR PROFESOR
# ============================================
@app.get("/api/insertar-alumnos-prueba")
async def insertar_alumnos_prueba():
    import psycopg2
    
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        if not DATABASE_URL:
            return {"success": False, "error": "DATABASE_URL no configurada"}
        
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cur = conn.cursor()
        
        # ========== ALUMNOS PARA LA PROFE ANA (grados 10 y 11) ==========
        alumnos_ana = [
            ('Valentina Rojas', 'valentina@email.com', 11, 95),
            ('Mateo Herrera', 'mateo@email.com', 10, 85),
            ('Sofia Ramirez', 'sofia@email.com', 11, 98),
            ('Isabella Torres', 'isabella@email.com', 11, 92),
            ('Camila Ortiz', 'camila@email.com', 10, 88),
            ('Lucas Mendoza', 'lucas@email.com', 10, 75),
            ('Daniela Paz', 'daniela@email.com', 11, 90),
        ]
        
        # ========== ALUMNOS PARA EL PROFE CARLOS (grados 8 y 9) ==========
        alumnos_carlos = [
            ('Samuel Gomez', 'samuel@email.com', 8, 78),
            ('Lucia Mendez', 'lucia@email.com', 9, 88),
            ('Diego Fernandez', 'diego@email.com', 8, 68),
            ('Javier Castro', 'javier@email.com', 9, 75),
            ('Andres Silva', 'andres@email.com', 8, 82),
            ('Carolina Reyes', 'carolina@email.com', 9, 91),
        ]
        
        # Insertar alumnos de Ana
        for alumno in alumnos_ana:
            cur.execute("""
                INSERT INTO alumnos (nombre, correo, grado, promedio) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (correo) DO NOTHING
            """, alumno)
        
        # Insertar alumnos de Carlos
        for alumno in alumnos_carlos:
            cur.execute("""
                INSERT INTO alumnos (nombre, correo, grado, promedio) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (correo) DO NOTHING
            """, alumno)
        
        cur.close()
        conn.close()
        
        return {
            "success": True, 
            "message": f"Insertados {len(alumnos_ana)} alumnos para Ana (grados 10-11) y {len(alumnos_carlos)} alumnos para Carlos (grados 8-9)",
            "total": len(alumnos_ana) + len(alumnos_carlos)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    # ============================================
# AGREGAR COLUMNA EXAMEN_NOMBRE A EVALUACION
# ============================================
@app.get("/api/agregar-columna-examen")
async def agregar_columna_examen():
    import psycopg2
    
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cur = conn.cursor()
        
        # Agregar columna examen_nombre
        cur.execute("ALTER TABLE evaluacion ADD COLUMN IF NOT EXISTS examen_nombre VARCHAR(200)")
        cur.execute("ALTER TABLE evaluacion ADD COLUMN IF NOT EXISTS confianza_validacion DECIMAL(5,2)")
        
        cur.close()
        conn.close()
        
        return {"success": True, "message": "Columnas agregadas correctamente"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    

    # ============================================
# CREAR PROFESOR CARLOS
# ============================================
@app.get("/api/crear-carlos")
async def crear_carlos():
    import psycopg2
    import bcrypt
    
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cur = conn.cursor()
        
        # Verificar si Carlos ya existe
        cur.execute("SELECT id_docente FROM docentes WHERE email = 'carlos@eduscan.com'")
        existe = cur.fetchone()
        
        if existe:
            # Actualizar contraseña a 123
            hash_pass = bcrypt.hashpw('123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute("UPDATE docentes SET password_hash = %s WHERE email = 'carlos@eduscan.com'", (hash_pass,))
            mensaje = "Carlos actualizado con contraseña 123"
        else:
            # Crear Carlos
            hash_pass = bcrypt.hashpw('123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute('''
                INSERT INTO docentes (nombre, email, password_hash, rol)
                VALUES (%s, %s, %s, %s)
            ''', ('Prof. Carlos Ruiz', 'carlos@eduscan.com', hash_pass, 'docente'))
            
            # Obtener el ID
            cur.execute("SELECT id_docente FROM docentes WHERE email = 'carlos@eduscan.com'")
            carlos_id = cur.fetchone()[0]
            
            # Asignar grados 8 y 9
            cur.execute('''
                INSERT INTO docente_grados (docente_id, grado) VALUES (%s, 8), (%s, 9)
                ON CONFLICT (docente_id, grado) DO NOTHING
            ''', (carlos_id, carlos_id))
            mensaje = "Carlos creado con éxito"
        
        cur.close()
        conn.close()
        
        return {"success": True, "message": mensaje}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    
# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)