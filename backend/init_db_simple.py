import psycopg2

DATABASE_URL = "postgresql://eduscan_user:BEAItZDgqRvBauTjKi52BYgGO7rZqAct@dpg-d7g54nhj2pic7386h040.oregon-postgres.render.com/eduscan_db_72hg"

modos_ssl = ['require', 'prefer', 'allow', 'disable']

for modo in modos_ssl:
    try:
        print(f"Probando sslmode={modo}...")
        conn = psycopg2.connect(DATABASE_URL, sslmode=modo, connect_timeout=5)
        print(f"✅ CONECTADO con sslmode={modo}")
        conn.close()
        break
    except Exception as e:
        print(f"❌ Falló con {modo}: {str(e)[:50]}")