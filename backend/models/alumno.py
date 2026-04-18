# backend/models/alumno.py
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Alumno(Base):
    __tablename__ = 'alumnos'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    grado = Column(Integer, nullable=False)  # 1 a 11
    calificacion = Column(Float, nullable=False)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)

class Examen(Base):
    __tablename__ = 'examenes'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String(200), nullable=False)
    grado = Column(Integer, nullable=False)
    asignatura = Column(String(100), nullable=False)
    fecha = Column(Date, nullable=False)
    qr_code = Column(String(50), unique=True, nullable=False)

class Escaneo(Base):
    __tablename__ = 'escaneos'
    
    id = Column(Integer, primary_key=True)
    alumno_id = Column(Integer, nullable=True)
    examen_id = Column(Integer, nullable=True)
    codigo_escaneado = Column(String(50), nullable=False)
    fecha_escaneo = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(20), default='exitoso')