# backend/api/alumnos.py
from fastapi import APIRouter, HTTPException
from typing import List
from ..models.alumno import Alumno
from ..services.database import get_db

router = APIRouter(prefix="/api/alumnos", tags=["Alumnos"])

@router.get("/")
async def get_alumnos():
    """Obtener todos los alumnos"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM alumnos ORDER BY calificacion DESC")
    alumnos = cursor.fetchall()
    cursor.close()
    return [{"id": a[0], "nombre": a[1], "email": a[2], "grado": a[3], "calificacion": a[4]} for a in alumnos]

@router.get("/{alumno_id}")
async def get_alumno(alumno_id: int):
    """Obtener un alumno específico"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM alumnos WHERE id = %s", (alumno_id,))
    alumno = cursor.fetchone()
    cursor.close()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return {"id": alumno[0], "nombre": alumno[1], "email": alumno[2], "grado": alumno[3], "calificacion": alumno[4]}

@router.post("/")
async def create_alumno(alumno: dict):
    """Crear nuevo alumno"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO alumnos (nombre, email, grado, calificacion) VALUES (%s, %s, %s, %s) RETURNING id",
        (alumno['nombre'], alumno['email'], alumno['grado'], alumno['calificacion'])
    )
    new_id = cursor.fetchone()[0]
    db.commit()
    cursor.close()
    return {"id": new_id, **alumno}

@router.put("/{alumno_id}")
async def update_alumno(alumno_id: int, alumno: dict):
    """Actualizar alumno"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE alumnos SET nombre=%s, email=%s, grado=%s, calificacion=%s WHERE id=%s",
        (alumno['nombre'], alumno['email'], alumno['grado'], alumno['calificacion'], alumno_id)
    )
    db.commit()
    cursor.close()
    return {"id": alumno_id, **alumno}

@router.delete("/{alumno_id}")
async def delete_alumno(alumno_id: int):
    """Eliminar alumno"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM alumnos WHERE id = %s", (alumno_id,))
    db.commit()
    cursor.close()
    return {"message": "Alumno eliminado"}