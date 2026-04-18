# backend/api/ia.py
from fastapi import APIRouter
import psycopg2
from psycopg2.extras import RealDictCursor
import os

router = APIRouter(prefix="/api/ia", tags=["IA"])

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/eduscan')

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@router.get("/recomendaciones")
async def get_recomendaciones():
    conn = get_db()
    cur = conn.cursor()
    
    # Alumnos con bajo rendimiento (menos de 70)
    cur.execute("""
        SELECT id, nombre, grado, calificacion 
        FROM alumnos 
        WHERE calificacion < 70 
        ORDER BY calificacion ASC 
        LIMIT 5
    """)
    alumnos_bajos = cur.fetchall()
    cur.close()
    conn.close()
    
    recomendaciones = []
    for a in alumnos_bajos:
        if a['calificacion'] < 50:
            prioridad = "Alta"
            mensaje = f"🔴 {a['nombre']} - Necesita tutoría URGENTE"
        elif a['calificacion'] < 60:
            prioridad = "Media-Alta"
            mensaje = f"⚠️ {a['nombre']} - Requiere refuerzo académico"
        else:
            prioridad = "Media"
            mensaje = f"📚 {a['nombre']} - Puede mejorar con práctica adicional"
        
        recomendaciones.append({
            "alumno_id": a['id'],
            "nombre": a['nombre'],
            "grado": a['grado'],
            "calificacion": a['calificacion'],
            "prioridad": prioridad,
            "recomendacion": mensaje
        })
    
    return recomendaciones

@router.get("/pronostico/{alumno_id}")
async def get_pronostico(alumno_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nombre, calificacion FROM alumnos WHERE id = %s", (alumno_id,))
    alumno = cur.fetchone()
    cur.close()
    conn.close()
    
    if not alumno:
        return {"error": "Alumno no encontrado"}
    
    nombre = alumno['nombre']
    nota = alumno['calificacion']
    
    if nota >= 90:
        mensaje = "🏆 Excelente - Potencial para Cuadro de Honor"
        color = "gold"
    elif nota >= 75:
        mensaje = "📈 Buen desempeño - Puede llegar a excelente"
        color = "blue"
    elif nota >= 60:
        mensaje = "⚠️ En riesgo - Requiere atención"
        color = "orange"
    else:
        mensaje = "🔴 Crítico - Necesita tutoría inmediata"
        color = "red"
    
    return {
        "nombre": nombre,
        "calificacion": nota,
        "pronostico": mensaje,
        "color": color
    }