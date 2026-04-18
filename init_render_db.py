"""
Inicializar base de datos PostgreSQL en Render
"""
import psycopg2
import os
import sys
from urllib.parse import urlparse

# Obtener URL de base de datos
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("‚ùå Error: DATABASE_URL no est√° configurada en .env")
    print("Ì≥ù Agrega: DATABASE_URL=postgresql://...")
    sys.exit(1)

print(f"Ì≥° Conectando a: {DATABASE_URL.replace('://', '://***:***@')}")

def init_database():
    try:
        # Conectar a PostgreSQL en Render
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("‚úÖ Conectado a PostgreSQL en Render")
        
        # ==========================================
        # CREAR TABLAS
        # ==========================================
        
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
        print("‚úÖ Tabla 'alumnos' creada")
        
        # Tabla evaluacion
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluacion (
                id_evaluacion SERIAL PRIMARY KEY,
                id_alumno INTEGER REFERENCES alumnos(id_alumno) ON DELETE CASCADE,
                puntaje DECIMAL(5,2),
                fecha DATE DEFAULT CURRENT_DATE,
                examen_nombre VARCHAR(200),
                feedback TEXT
            )
        """)
        print("‚úÖ Tabla 'evaluacion' creada")
        
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
        print("‚úÖ Tabla 'pregunta' creada")
        
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
        print("‚úÖ Tabla 'respuesta' creada")
        
        # ==========================================
        # INSERTAR DATOS DE EJEMPLO (si no existen)
        # ==========================================
        
        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM alumnos")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("\nÌ≥ù Insertando datos de ejemplo...")
            
            # Insertar alumnos
            alumnos_data = [
                ('Carlos Ramirez', 'carlos@gmail.com', 10, 85.5, '3001234567'),
                ('Laura Torres', 'laura@gmail.com', 11, 92.0, '3001234568'),
                ('Andres Lopez', 'andres@gmail.com', 9, 78.5, '3001234569'),
                ('Sofia Martinez', 'sofia@gmail.com', 10, 88.0, '3001234570'),
                ('Daniela Rojas', 'daniela@gmail.com', 11, 95.5, '3001234571'),
                ('Luis Fernandez', 'luis@gmail.com', 8, 72.0, '3001234572'),
                ('Camila Vargas', 'camila@gmail.com', 10, 91.0, '3001234573'),
                ('Miguel Castro', 'miguel@gmail.com', 9, 76.5, '3001234574'),
                ('Valentina Ruiz', 'valentina@gmail.com', 11, 98.0, '3001234575'),
                ('Sebastian Herrera', 'sebastian@gmail.com', 10, 84.0, '3001234576')
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
                (1, 4.5, '2026-04-12', 'Examen Matem√°ticas'),
                (2, 3.8, '2026-04-12', 'Examen Ciencias'),
                (3, 5.0, '2026-04-13', 'Examen General'),
                (4, 2.5, '2026-04-13', 'Examen Historia'),
                (5, 4.2, '2026-04-14', 'Examen Matem√°ticas'),
            ]
            
            for eval_data in evaluaciones_data:
                cursor.execute("""
                    INSERT INTO evaluacion (id_alumno, puntaje, fecha, examen_nombre)
                    VALUES (%s, %s, %s, %s)
                """, eval_data)
            print("  ‚úÖ 5 evaluaciones insertadas")
            
            conn.commit()
            print("\nÌæâ Datos de ejemplo insertados exitosamente")
        
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
        
        conn.close()
        print("\n‚úÖ Inicializaci√≥n completada con √©xito")
        
    except Exception as e:
        print(f"‚ùå Error: {e}")
        print("\nÌ≤° Soluciones:")
        print("  1. Verifica que DATABASE_URL sea correcta")
        print("  2. Asegura que la IP de Render est√© permitida")
        print("  3. Revisa que la base de datos exista")
        sys.exit(1)

if __name__ == "__main__":
    print("Ì∫Ä Inicializando base de datos en Render...")
    init_database()
