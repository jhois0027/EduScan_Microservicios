# backend/api/examenes.py
from fastapi import APIRouter, HTTPException
from ..services.database import get_db

router = APIRouter(prefix="/api/examenes", tags=["Exámenes"])

@router.get("/")
async def get_examenes():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM examenes ORDER BY fecha DESC")
    examenes = cursor.fetchall()
    cursor.close()
    return [{"id": e[0], "titulo": e[1], "grado": e[2], "asignatura": e[3], "fecha": str(e[4]), "qr_code": e[5]} for e in examenes]

@router.get("/validar/{codigo}")
async def validar_qr(codigo: str):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM examenes WHERE qr_code = %s", (codigo,))
    examen = cursor.fetchone()
    cursor.close()
    if examen:
        return {"valido": True, "examen": {"id": examen[0], "titulo": examen[1], "grado": examen[2], "asignatura": examen[3], "fecha": str(examen[4]), "qr_code": examen[5]}}
    return {"valido": False, "mensaje": "Código no válido"}

@router.post("/")
async def create_examen(examen: dict):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO examenes (titulo, grado, asignatura, fecha, qr_code) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (examen['titulo'], examen['grado'], examen['asignatura'], examen['fecha'], examen.get('qr_code', f"EXAM-{hash(examen['titulo'])%1000}"))
    )
    new_id = cursor.fetchone()[0]
    db.commit()
    cursor.close()
    return {"id": new_id, **examen}