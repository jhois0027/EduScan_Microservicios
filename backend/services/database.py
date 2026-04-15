from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import mysql.connector
from mysql.connector import Error

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración CORRECTA para tu MySQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'evaluacion_ia',
    'user': 'root',
    'password': 'root'  # Tu contraseña
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

@app.get("/health")
async def health():
    conn = get_db_connection()
    if conn and conn.is_connected():
        conn.close()
        return {"status": "healthy", "database": "connected", "message": "MySQL conectado correctamente"}
    return {"status": "unhealthy", "database": "disconnected", "error": "No se pudo conectar a MySQL"}

@app.get("/alumnos")
async def get_alumnos():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexion a MySQL")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_alumno, nombre, correo FROM alumnos")
    alumnos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {"alumnos": alumnos}

@app.get("/evaluaciones")
async def get_evaluaciones():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.id_evaluacion, a.nombre as alumno, e.puntaje, e.fecha
        FROM evaluacion e
        JOIN alumnos a ON e.id_alumno = a.id_alumno
        ORDER BY e.fecha DESC
    """)
    
    evaluaciones = cursor.fetchall()
    for ev in evaluaciones:
        if ev['fecha']:
            ev['fecha'] = str(ev['fecha'])
    
    cursor.close()
    conn.close()
    
    return {"evaluaciones": evaluaciones}

@app.get("/dashboard/resumen")
async def dashboard_resumen():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as total FROM alumnos")
    total_alumnos = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM evaluacion")
    total_evaluaciones = cursor.fetchone()['total']
    
    cursor.execute("SELECT AVG(puntaje) as promedio FROM evaluacion")
    promedio = cursor.fetchone()['promedio'] or 0
    
    cursor.execute("SELECT MAX(puntaje) as mejor FROM evaluacion")
    mejor_nota = cursor.fetchone()['mejor'] or 0
    
    cursor.execute("""
        SELECT a.nombre, AVG(e.puntaje) as promedio
        FROM alumnos a
        JOIN evaluacion e ON a.id_alumno = e.id_alumno
        GROUP BY a.id_alumno
        ORDER BY promedio DESC
        LIMIT 5
    """)
    top_alumnos = cursor.fetchall()
    for t in top_alumnos:
        t['promedio'] = round(t['promedio'], 2)
    
    cursor.close()
    conn.close()
    
    return {
        "estadisticas": {
            "total_alumnos": total_alumnos,
            "total_evaluaciones": total_evaluaciones,
            "promedio_general": round(promedio, 2),
            "mejor_nota": round(mejor_nota, 2)
        },
        "top_alumnos": top_alumnos
    }

@app.get("/alumno/{alumno_id}/detalle")
async def alumno_detalle(alumno_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexion")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id_alumno, nombre, correo FROM alumnos WHERE id_alumno = %s", (alumno_id,))
    alumno = cursor.fetchone()
    
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    cursor.execute("""
        SELECT id_evaluacion, puntaje, fecha 
        FROM evaluacion 
        WHERE id_alumno = %s 
        ORDER BY fecha DESC
    """, (alumno_id,))
    
    evaluaciones = cursor.fetchall()
    for ev in evaluaciones:
        ev['fecha'] = str(ev['fecha'])
    
    cursor.execute("""
        SELECT AVG(puntaje) as promedio, COUNT(*) as total 
        FROM evaluacion 
        WHERE id_alumno = %s
    """, (alumno_id,))
    stats = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return {
        "alumno": alumno,
        "evaluaciones": evaluaciones,
        "promedio": round(stats['promedio'], 2) if stats['promedio'] else 0,
        "total_evaluaciones": stats['total'] or 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
