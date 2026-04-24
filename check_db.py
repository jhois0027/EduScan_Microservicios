import psycopg2

DATABASE_URL = "postgresql://eduscan_user:BEAItZDgqRvBauTjKi52BYgGO7rZqAct@dpg-d7g54nhj2pic7386h040-a:5432/eduscan_db_72hg?sslmode=require"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Ver docentes
    cursor.execute("SELECT id_docente, nombre, email, password_hash FROM docentes")
    print("Ì≥ã DOCENTES REGISTRADOS:")
    for row in cursor.fetchall():
        print(f"   ID: {row[0]}, Nombre: {row[1]}, Email: {row[2]}")
        print(f"   Hash: {row[3][:50]}...")
        print()
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"‚ùå Error: {e}")
