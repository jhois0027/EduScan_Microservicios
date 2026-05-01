import psycopg2
import os

# Cargar desde .env
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('DATABASE_URL='):
            DATABASE_URL = line.strip().split('=', 1)[1]
            break

def init():
    try:
        print("🔌 Conectando...")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cur = conn.cursor()
        
        print("✅ Conectado")
        
        # Crear tablas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS docentes (
                id_docente SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(50) DEFAULT 'docente'
            )
        """)
        print("✅ Tabla docentes")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS docente_grados (
                id SERIAL PRIMARY KEY,
                docente_id INTEGER REFERENCES docentes(id_docente),
                grado INTEGER NOT NULL,
                UNIQUE(docente_id, grado)
            )
        """)
        print("✅ Tabla docente_grados")
        
        # Insertar docentes
        hash_pass = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtXEyMqCqB7QK'
        cur.execute("""
            INSERT INTO docentes (nombre, email, password_hash, rol) VALUES
            ('Prof. Ana Lopez', 'ana@eduscan.com', %s, 'docente'),
            ('Prof. Carlos Ruiz', 'carlos@eduscan.com', %s, 'docente'),
            ('Administrador', 'admin@eduscan.com', %s, 'admin')
            ON CONFLICT (email) DO NOTHING
        """, (hash_pass, hash_pass, hash_pass))
        print("✅ Docentes insertados")
        
        # Asignar grados
        cur.execute("SELECT id_docente FROM docentes WHERE email = 'ana@eduscan.com'")
        ana = cur.fetchone()
        cur.execute("SELECT id_docente FROM docentes WHERE email = 'carlos@eduscan.com'")
        carlos = cur.fetchone()
        
        if ana and carlos:
            cur.execute("""
                INSERT INTO docente_grados (docente_id, grado) VALUES
                (%s, 10), (%s, 11), (%s, 8), (%s, 9)
                ON CONFLICT (docente_id, grado) DO NOTHING
            """, (ana[0], ana[0], carlos[0], carlos[0]))
            print("✅ Grados asignados")
        
        # Mostrar resultados
        cur.execute("SELECT nombre, email, rol FROM docentes")
        print("\n📋 Docentes:")
        for row in cur.fetchall():
            print(f"   {row[0]} | {row[1]} | {row[2]}")
        
        cur.close()
        conn.close()
        print("\n✅ Todo listo!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    init()