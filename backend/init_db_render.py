"""
Inicializar base de datos PostgreSQL en Render
"""
import psycopg2
import os
import sys
from datetime import datetime

# Obtener URL de base de datos
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("‚ùå Error: DATABASE_URL no est√° configurada en .env")
    print("Ì≥ù Agrega: DATABASE_URL=postgresql://...")
    sys.exit(1)

# Ocultar credenciales en logs
safe_url = DATABASE_URL.replace('://', '://***:***@') if '@' in DATABASE_URL else DATABASE_URL
print(f"Ì≥° Conectando a: {safe_url.split('@')[0]}@***")

def init_database():
    conn = None
    try:
        # Conectar a PostgreSQL en Render con timeout
        conn = psycopg2.connect(DATABASE_URL, sslmode='require', connect_timeout=10)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("‚úÖ Conectado a PostgreSQL en Render")
        
        # ==========================================
        # CREAR TABLAS (con IF NOT EXISTS)
        # ==========================================
        
        print("\nÌ≥ã Creando tablas...")
        
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
        print("  ‚úÖ Tabla 'alumnos'")
        
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
        print("  ‚úÖ Tabla 'evaluacion'")
        
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
        print("  ‚úÖ Tabla 'pregunta'")
        
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
        print("  ‚úÖ Tabla 'respuesta'")
        
        # ==========================================
        # INSERTAR DATOS DE EJEMPLO (solo si no existen)
        # ==========================================
        
        cursor.execute("SELECT COUNT(*) FROM alumnos")
        count_alumnos = cursor.fetchone()[0]
        
        if count_alumnos == 0:
            print("\nÌ≥ù Insertando datos de ejemplo...")
            
            # Insertar alumnos
            alumnos_data = [
                ('Valentina Rojas', 'valentina@email.com', 11, 98.0, '3001234567'),
                ('Mateo Herrera', 'mateo@email.com', 10, 85.0, '3001234568'),
                ('Sofia Ramirez', 'sofia@email.com', 11, 96.0, '3001234569'),
                ('Isabella Torres', 'isabella@email.com', 11, 100.0, '3001234570'),
                ('Samuel Gomez', 'samuel@email.com', 8, 78.0, '3001234571'),
                ('Camila Ortiz', 'camila@email.com', 10, 92.0, '3001234572'),
                ('Diego Fernandez', 'diego@email.com', 7, 68.0, '3001234573'),
                ('Lucia Mendez', 'lucia@email.com', 9, 88.0, '3001234574'),
                ('Javier Castro', 'javier@email.com', 6, 75.0, '3001234575'),
                ('Daniela Paz', 'daniela@email.com', 5, 82.0, '3001234576')
            ]
            
            for alumno in alumnos_data:
                cursor.execute("""
                    INSERT INTO alumnos (nombre, correo, grado, promedio, telefono)
                    VALUES (%s, %s, %s, %s, %s)
                """, alumno)
            print("  ‚úÖ 10 alumnos insertados")
            
            # Insertar preguntas
            preguntas_data = [
                ('2 + 2 = ?', '4', 'Matem√°ticas', 1),
                ('5 x 3 = ?', '15', 'Matem√°ticas', 1),
                ('10 - 6 = ?', '4', 'Matem√°ticas', 1),
                ('Capital de Colombia', 'Bogota', 'Geograf√≠a', 1),
                ('Color del cielo en un dia despejado', 'Azul', 'Ciencias', 1),
                ('3 + 7 = ?', '10', 'Matem√°ticas', 1),
                ('9 x 2 = ?', '18', 'Matem√°ticas', 1),
                ('15 / 3 = ?', '5', 'Matem√°ticas', 1),
                ('Raiz cuadrada de 16', '4', 'Matem√°ticas', 1),
                ('Cuantos dias tiene una semana', '7', 'General', 1)
            ]
            
            for pregunta in preguntas_data:
                cursor.execute("""
                    INSERT INTO pregunta (descripcion, respuesta_correcta, materia, puntos)
                    VALUES (%s, %s, %s, %s)
                """, pregunta)
            print("  ‚úÖ 10 preguntas insertadas")
            
            # Insertar evaluaciones
            evaluaciones_data = [
                (1, 95.0, '2026-04-12', 'Examen Matem√°ticas', 'Excelente trabajo'),
                (2, 85.0, '2026-04-12', 'Examen Matem√°ticas', 'Buen desempe√±o'),
                (3, 98.0, '2026-04-13', 'Examen Lengua', 'Sobresaliente'),
                (4, 100.0, '2026-04-13', 'Examen Lengua', 'Perfecto'),
                (5, 78.0, '2026-04-14', 'Examen Ciencias', 'Aprobado'),
            ]
            
            for eval_data in evaluaciones_data:
                cursor.execute("""
                    INSERT INTO evaluacion (id_alumno, puntaje, fecha, examen_nombre, feedback)
                    VALUES (%s, %s, %s, %s, %s)
                """, eval_data)
            print("  ‚úÖ 5 evaluaciones insertadas")
            
            conn.commit()
            print("\nÌæâ Datos de ejemplo insertados exitosamente")
        else:
            print(f"\nÌ≥ä Base de datos ya inicializada con {count_alumnos} alumnos")
        
        # ==========================================
        # MOSTRAR ESTAD√çSTICAS
        # ==========================================
        print("\n" + "="*50)
        print("Ì≥ä ESTAD√çSTICAS DE LA BASE DE DATOS")
        print("="*50)
        
        cursor.execute("""
            SELECT 'Alumnos' as tabla, COUNT(*) as total FROM alumnos
            UNION ALL SELECT 'Evaluaciones', COUNT(*) FROM evaluacion
            UNION ALL SELECT 'Preguntas', COUNT(*) FROM pregunta
            UNION ALL SELECT 'Respuestas', COUNT(*) FROM respuesta
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} registros")
        
        cursor.close()
        conn.close()
        
        print("\n‚úÖ Inicializaci√≥n completada con √©xito")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"‚ùå Error de conexi√≥n: {e}")
        print("\nÌ≤° Soluciones:")
        print("  1. Verifica que la base de datos en Render est√© activa")
        print("  2. Confirma que DATABASE_URL es correcta")
        print("  3. Asegura que las variables de entorno est√©n configuradas")
        return False
        
    except Exception as e:
        print(f"‚ùå Error: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Ì∫Ä Inicializando base de datos en Render...")
    print("="*50)
    success = init_database()
    if not success:
        sys.exit(1)
