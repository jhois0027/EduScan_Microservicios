from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# ✅ CORS (OBLIGATORIO para tu dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DB ----------------

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="evaluacion_ia"
    )

# ---------------- MODELOS ----------------

class Alumno(BaseModel):
    nombre: str
    correo: str

class Modulo(BaseModel):
    nombre: str
    descripcion: str = ""
    color: str = "#3b82f6"

class Examen(BaseModel):
    nombre: str
    id_modulo: int
    fecha: str

# ---------------- ESTADISTICAS (🔥 LO QUE TE FALTABA) ----------------

@app.get("/estadisticas")
def estadisticas():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Total alumnos
    cursor.execute("SELECT COUNT(*) as total FROM alumnos")
    total_alumnos = cursor.fetchone()["total"]

    # Total examenes
    cursor.execute("SELECT COUNT(*) as total FROM examenes")
    total_examenes = cursor.fetchone()["total"]

    # Promedio notas (si tienes tabla evaluaciones)
    try:
        cursor.execute("SELECT AVG(puntaje) as promedio FROM evaluaciones")
        promedio = cursor.fetchone()["promedio"] or 0

        cursor.execute("SELECT MAX(puntaje) as maximo FROM evaluaciones")
        maximo = cursor.fetchone()["maximo"] or 0
    except:
        promedio = 0
        maximo = 0

    db.close()

    return {
        "total_alumnos": total_alumnos,
        "total_evaluaciones": total_examenes,
        "promedio_general": round(promedio, 2),
        "mejor_nota": maximo
    }

# ---------------- ALUMNOS ----------------

@app.get("/alumnos")
def get_alumnos():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alumnos")
    data = cursor.fetchall()
    db.close()
    return {"alumnos": data}

@app.post("/alumnos")
def crear_alumno(alumno: Alumno):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO alumnos (nombre, correo) VALUES (%s,%s)",
        (alumno.nombre, alumno.correo)
    )
    db.commit()
    db.close()
    return {"msg": "ok"}

@app.put("/alumnos/{id}")
def editar_alumno(id: int, alumno: Alumno):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE alumnos SET nombre=%s, correo=%s WHERE id_alumno=%s",
        (alumno.nombre, alumno.correo, id)
    )
    db.commit()
    db.close()
    return {"msg": "ok"}

@app.delete("/alumnos/{id}")
def eliminar_alumno(id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM alumnos WHERE id_alumno=%s", (id,))
    db.commit()
    db.close()
    return {"msg": "ok"}

# ---------------- MODULOS ----------------

@app.get("/modulos")
def get_modulos():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM modulos")
    data = cursor.fetchall()
    db.close()
    return {"modulos": data}

@app.post("/modulos")
def crear_modulo(modulo: Modulo):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO modulos (nombre, descripcion, color) VALUES (%s,%s,%s)",
        (modulo.nombre, modulo.descripcion, modulo.color)
    )
    db.commit()
    db.close()
    return {"msg": "ok"}

@app.put("/modulos/{id}")
def editar_modulo(id: int, modulo: Modulo):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE modulos SET nombre=%s, descripcion=%s, color=%s WHERE id_modulo=%s",
        (modulo.nombre, modulo.descripcion, modulo.color, id)
    )
    db.commit()
    db.close()
    return {"msg": "ok"}

@app.delete("/modulos/{id}")
def eliminar_modulo(id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM modulos WHERE id_modulo=%s", (id,))
    db.commit()
    db.close()
    return {"msg": "ok"}

# ---------------- EXAMENES ----------------

@app.get("/examenes")
def get_examenes():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.*, m.nombre as modulo_nombre
        FROM examenes e
        JOIN modulos m ON e.id_modulo = m.id_modulo
    """)
    data = cursor.fetchall()
    db.close()
    return {"examenes": data}

@app.post("/examenes")
def crear_examen(examen: Examen):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO examenes (nombre, id_modulo, fecha) VALUES (%s,%s,%s)",
        (examen.nombre, examen.id_modulo, examen.fecha)
    )
    db.commit()
    db.close()
    return {"msg": "ok"}

@app.put("/examenes/{id}")
def editar_examen(id: int, examen: Examen):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE examenes SET nombre=%s, id_modulo=%s, fecha=%s WHERE id_examen=%s",
        (examen.nombre, examen.id_modulo, examen.fecha, id)
    )
    db.commit()
    db.close()
    return {"msg": "ok"}

@app.delete("/examenes/{id}")
def eliminar_examen(id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM examenes WHERE id_examen=%s", (id,))
    db.commit()
    db.close()
    return {"msg": "ok"}