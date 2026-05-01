"""
Inicializar base de datos PostgreSQL en Render
"""
import psycopg2
import os
import sys
from datetime import datetime

# USAR VARIABLE DE ENTORNO (NO hardcodear)
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL no está configurada")
    print("   Configura la variable de entorno o usa:")
    print("   export DATABASE_URL='postgresql://...'")
    sys.exit(1)

print(f"🔌 Conectando a: {DATABASE_URL.split('@')[0].replace('://', '://***:***@')}@***")

def init_database():
    conn = None
    try:
        # Conectar SIN SSL
        conn = psycopg2.connect(DATABASE_URL, sslmode='require', connect_timeout=30)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Conectado a PostgreSQL en Render")
        
        # ==========================================
        # CREAR TABLAS
        # ==========================================
        
        print("\n📦 Creando tablas...")
        
        # Tabla alumnos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alumnos (
                id_alumno SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) UNIQUE,
                grado INTEGER DEFAULT 10,
                promedio DECIMAL(5,2) DEFAULT 0,
                telefono VARCHAR(20),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Tabla 'alumnos'")
        
        # Tabla evaluacion
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluacion (
                id_evaluacion SERIAL PRIMARY KEY,
                id_alumno INTEGER REFERENCES alumnos(id_alumno) ON DELETE CASCADE,
                puntaje DECIMAL(5,2),
                fecha DATE DEFAULT CURRENT_DATE,
                examen_nombre VARCHAR(200),
                feedback TEXT,
                confianza_validacion DECIMAL(5,2)
            )
        """)
        print("  ✅ Tabla 'evaluacion'")
        
        # Tabla pregunta
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pregunta (
                id_pregunta SERIAL PRIMARY KEY,
                descripcion TEXT NOT NULL,
                respuesta_correcta VARCHAR(50) NOT NULL,
                materia VARCHAR(50) DEFAULT 'General',
                puntos INTEGER DEFAULT 1
            )
        """)
        print("  ✅ Tabla 'pregunta'")
        
        # Tabla respuesta
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS respuesta (
                id_respuesta SERIAL PRIMARY KEY,
                id_evaluacion INTEGER REFERENCES evaluacion(id_evaluacion) ON DELETE CASCADE,
                id_pregunta INTEGER REFERENCES pregunta(id_pregunta) ON DELETE CASCADE,
                es_correcta BOOLEAN DEFAULT FALSE,
                respuesta_alumno VARCHAR(50)
            )
        """)
        print("  ✅ Tabla 'respuesta'")
        
        # Tabla docentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS docentes (
                id_docente SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(50) DEFAULT 'docente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Tabla 'docentes'")
        
        # Tabla docente_grados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS docente_grados (
                id SERIAL PRIMARY KEY,
                docente_id INTEGER REFERENCES docentes(id_docente) ON DELETE CASCADE,
                grado INTEGER NOT NULL,
                UNIQUE(docente_id, grado)
            )
        """)
        print("  ✅ Tabla 'docente_grados'")
        
        # ==========================================
        # INSERTAR DATOS DE EJEMPLO
        # ==========================================
        
        # Docentes
        cursor.execute("SELECT COUNT(*) FROM docentes")
        if cursor.fetchone()[0] == 0:
            print("\n📝 Insertando docentes...")
            hash_pass = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtXEyMqCqB7QK'
            
            cursor.execute("""
                INSERT INTO docentes (nombre, email, password_hash, rol) VALUES
                ('Prof. Ana Lopez', 'ana@eduscan.com', %s, 'docente'),
                ('Prof. Carlos Ruiz', 'carlos@eduscan.com', %s, 'docente'),
                ('Administrador', 'admin@eduscan.com', %s, 'admin')
                ON CONFLICT (email) DO NOTHING
            """, (hash_pass, hash_pass, hash_pass))
            print("  ✅ Docentes insertados")
            
            # Asignar grados
            cursor.execute("SELECT id_docente FROM docentes WHERE email = 'ana@eduscan.com'")
            ana = cursor.fetchone()
            cursor.execute("SELECT id_docente FROM docentes WHERE email = 'carlos@eduscan.com'")
            carlos = cursor.fetchone()
            
            if ana and carlos:
                cursor.execute("""
                    INSERT INTO docente_grados (docente_id, grado) VALUES
                    (%s, 10), (%s, 11), (%s, 8), (%s, 9)
                    ON CONFLICT (docente_id, grado) DO NOTHING
                """, (ana[0], ana[0], carlos[0], carlos[0]))
                print("  ✅ Grados asignados")
        
        conn.commit()
        
        # ==========================================
        # MOSTRAR ESTADÍSTICAS
        # ==========================================
        print("\n" + "="*50)
        print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
        print("="*50)
        
        cursor.execute("""
            SELECT 'Alumnos' as tabla, COUNT(*) as total FROM alumnos
            UNION ALL SELECT 'Evaluaciones', COUNT(*) FROM evaluacion
            UNION ALL SELECT 'Preguntas', COUNT(*) FROM pregunta
            UNION ALL SELECT 'Respuestas', COUNT(*) FROM respuesta
            UNION ALL SELECT 'Docentes', COUNT(*) FROM docentes
            UNION ALL SELECT 'Docente_Grados', COUNT(*) FROM docente_grados
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} registros")
        
        cursor.execute("SELECT nombre, email, rol FROM docentes")
        print("\n👨‍🏫 DOCENTES:")
        for row in cursor.fetchall():
            print(f"   {row[0]} | {row[1]} | {row[2]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Inicialización completada")
        print("\n🔑 CREDENCIALES: ana@eduscan.com / password123")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión: {e}")
        print("\n��� Soluciones:")
        print("  1. Verifica que la base de datos en Render esté activa")
        print("  2. Confirma que DATABASE_URL es correcta")
        print("  3. Asegura que las variables de entorno estén configuradas")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Inicializando base de datos en Render...")
    print("="*50)
    success = init_database()
    if not success:
        sys.exit(1)
