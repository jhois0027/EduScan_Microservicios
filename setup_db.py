import psycopg2
import bcrypt
from urllib.parse import urlparse

# Tu URL de PostgreSQL (usa la que tienes)
DATABASE_URL = "postgresql://eduscan_user:BEAItZDgqRvBauTjKi52BYgGO7rZqAct@dpg-d7g54nhj2pic7386h040-a/eduscan_db_72hg"

def setup_database():
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("‚úÖ Conectado a PostgreSQL")
        
        # 1. Crear tabla de docentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS docentes (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(50) DEFAULT 'docente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("‚úÖ Tabla 'docentes' creada")
        
        # 2. Crear tabla de relaci√≥n docente-grados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS docente_grados (
                id SERIAL PRIMARY KEY,
                docente_id INTEGER REFERENCES docentes(id) ON DELETE CASCADE,
                grado INTEGER NOT NULL,
                UNIQUE(docente_id, grado)
            )
        """)
        print("‚úÖ Tabla 'docente_grados' creada")
        
        # 3. Agregar columna docente_id a alumnos (si no existe)
        try:
            cursor.execute("""
                ALTER TABLE alumnos ADD COLUMN IF NOT EXISTS docente_id INTEGER REFERENCES docentes(id)
            """)
            print("‚úÖ Columna 'docente_id' agregada a alumnos")
        except:
            print("‚ö†Ô∏è La columna ya existe o no se pudo agregar")
        
        # 4. Hashear contrase√±a (password123)
        password = "password123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 5. Insertar docentes
        docentes = [
            ('Prof. Ana L√≥pez', 'ana@eduscan.com', hashed, 'docente'),
            ('Prof. Carlos Ruiz', 'carlos@eduscan.com', hashed, 'docente'),
            ('Administrador', 'admin@eduscan.com', hashed, 'admin')
        ]
        
        for docente in docentes:
            cursor.execute("""
                INSERT INTO docentes (nombre, email, password_hash, rol) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
            """, docente)
        print("‚úÖ Docentes insertados")
        
        # 6. Asignar grados a docentes
        asignaciones = [
            (1, 10), (1, 11),  # Ana: grados 10 y 11
            (2, 8), (2, 9)      # Carlos: grados 8 y 9
        ]
        
        for docente_id, grado in asignaciones:
            cursor.execute("""
                INSERT INTO docente_grados (docente_id, grado) 
                VALUES (%s, %s)
                ON CONFLICT (docente_id, grado) DO NOTHING
            """, (docente_id, grado))
        print("‚úÖ Grados asignados a docentes")
        
        # 7. Verificar
        cursor.execute("SELECT id, nombre, email, rol FROM docentes")
        docentes_result = cursor.fetchall()
        print("\nÌ≥ã Docentes registrados:")
        for d in docentes_result:
            print(f"   ID: {d[0]} | Nombre: {d[1]} | Email: {d[2]} | Rol: {d[3]}")
        
        cursor.execute("SELECT docente_id, grado FROM docente_grados ORDER BY docente_id, grado")
        asignaciones_result = cursor.fetchall()
        print("\nÌ≥ã Asignaciones:")
        for a in asignaciones_result:
            print(f"   Docente ID: {a[0]} | Grado: {a[1]}¬∞")
        
        cursor.close()
        conn.close()
        
        print("\nÌæâ ¬°Todo listo! Las tablas fueron creadas exitosamente.")
        print("\nÌ¥ë Credenciales de prueba:")
        print("   ana@eduscan.com / password123 (Ve grados 10¬∞ y 11¬∞)")
        print("   carlos@eduscan.com / password123 (Ve grados 8¬∞ y 9¬∞)")
        print("   admin@eduscan.com / password123 (Ve todo)")
        
    except Exception as e:
        print(f"‚ùå Error: {e}")

if __name__ == "__main__":
    setup_database()
