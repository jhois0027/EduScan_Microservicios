import os
import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db():
    return await asyncpg.connect(DATABASE_URL)

@app.on_event("startup")
async def startup():
    conn = await get_db()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id_alumno SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            correo VARCHAR(100) UNIQUE
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS modulos (
            id_modulo SERIAL PRIMARY KEY,
            nombre VARCHAR(100) UNIQUE NOT NULL,
            descripcion TEXT,
            color VARCHAR(20)
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS examenes (
            id_examen SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            id_modulo INT REFERENCES modulos(id_modulo),
            fecha DATE,
            total_preguntas INT
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS pregunta (
            id_pregunta SERIAL PRIMARY KEY,
            descripcion TEXT,
            respuesta_correcta VARCHAR(50)
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS evaluacion (
            id_evaluacion SERIAL PRIMARY KEY,
            id_alumno INT REFERENCES alumnos(id_alumno),
            puntaje DECIMAL(5,2),
            fecha DATE
        )
    """)
    await conn.close()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/alumnos")
async def get_alumnos():
    conn = await get_db()
    rows = await conn.fetch("SELECT id_alumno, nombre, correo FROM alumnos ORDER BY id_alumno")
    await conn.close()
    return {"alumnos": [dict(row) for row in rows]}

@app.get("/modulos")
async def get_modulos():
    conn = await get_db()
    rows = await conn.fetch("SELECT id_modulo, nombre, descripcion, color FROM modulos ORDER BY id_modulo")
    await conn.close()
    return {"modulos": [dict(row) for row in rows]}

@app.get("/examenes")
async def get_examenes():
    conn = await get_db()
    rows = await conn.fetch("""
        SELECT e.id_examen, e.nombre, e.fecha, e.total_preguntas, m.nombre as modulo_nombre
        FROM examenes e
        JOIN modulos m ON e.id_modulo = m.id_modulo
        ORDER BY e.id_examen
    """)
    await conn.close()
    return {"examenes": [dict(row) for row in rows]}

@app.get("/estadisticas")
async def get_estadisticas():
    conn = await get_db()
    total_alumnos = await conn.fetchval("SELECT COUNT(*) FROM alumnos")
    total_evaluaciones = await conn.fetchval("SELECT COUNT(*) FROM evaluacion") or 0
    promedio = await conn.fetchval("SELECT AVG(puntaje) FROM evaluacion") or 0
    mejor = await conn.fetchval("SELECT MAX(puntaje) FROM evaluacion") or 0
    await conn.close()
    return {
        "total_alumnos": total_alumnos,
        "total_evaluaciones": total_evaluaciones,
        "promedio_general": round(promedio, 2),
        "mejor_nota": round(mejor, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
