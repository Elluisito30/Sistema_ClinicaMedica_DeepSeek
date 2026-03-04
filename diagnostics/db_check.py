import os
import sys
import socket
from datetime import datetime
from dotenv import load_dotenv
import psycopg2

def check_env():
    load_dotenv()
    info = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD_set": "yes" if os.getenv("DB_PASSWORD") else "no",
        "PG_DUMP_PATH_exists": os.path.exists(os.getenv("PG_DUMP_PATH", "")),
        "BACKUP_PATH_exists": os.path.isdir(os.getenv("BACKUP_PATH", "")),
    }
    return info

def tcp_ping(host, port, timeout=3):
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except Exception:
        return False

def connect_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "db_clinica"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            connect_timeout=5,
        )
        return conn
    except Exception as e:
        return str(e)

def run_checks():
    env = check_env()
    print("=== Diagnóstico de Conexión PostgreSQL ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Host: {env['DB_HOST']}")
    print(f"Port: {env['DB_PORT']}")
    print(f"DB: {env['DB_NAME']}")
    print(f"User: {env['DB_USER']}")
    print(f"Password set: {env['DB_PASSWORD_set']}")
    print(f"PG_DUMP_PATH exists: {env['PG_DUMP_PATH_exists']}")
    print(f"BACKUP_PATH exists: {env['BACKUP_PATH_exists']}")
    if not tcp_ping(env["DB_HOST"], env["DB_PORT"]):
        print("TCP: puerto no accesible")
    else:
        print("TCP: puerto accesible")
    conn = connect_db()
    if isinstance(conn, str):
        print("Conexión: ERROR")
        print(conn)
        sys.exit(1)
    print("Conexión: OK")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    ver = cur.fetchone()
    print(f"PostgreSQL version: {ver[0]}")
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name LIMIT 20;")
    tables = [r[0] for r in cur.fetchall()]
    print("Tablas encontradas:", ", ".join(tables) if tables else "ninguna")
    required = ["usuarios", "roles", "permisos", "especialidades", "consultorios", "medicos", "pacientes"]
    missing = [t for t in required if t not in tables]
    print("Faltantes:", ", ".join(missing) if missing else "ninguna")
    cur.execute("SELECT COUNT(*) FROM usuarios;")
    total_users = cur.fetchone()[0]
    print(f"Total usuarios: {total_users}")
    if total_users > 0:
        cur.execute("SELECT nombre_usuario, email, activo FROM usuarios ORDER BY fecha_creacion DESC NULLS LAST LIMIT 10;")
        rows = cur.fetchall()
        for u in rows:
            print(f"Usuario: {u[0]} | Email: {u[1]} | Activo: {u[2]}")
    cur.execute("SELECT 1;")
    print("Query simple: OK")
    cur.close()
    conn.close()
    print("=== Fin diagnóstico ===")

if __name__ == "__main__":
    run_checks()
