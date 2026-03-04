import os
import sys
from dotenv import load_dotenv
import psycopg2
import bcrypt

def main():
    if len(sys.argv) < 3:
        print("Uso: python diagnostics/set_user_password.py <usuario> <contraseña>")
        sys.exit(1)
    username = sys.argv[1]
    plaintext = sys.argv[2]
    load_dotenv()
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "db_clinica"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (username,))
    row = cur.fetchone()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plaintext.encode("utf-8"), salt).decode("utf-8")
    if row:
        user_id = row[0]
        cur.execute(
            "UPDATE usuarios SET hash_contraseña=%s, intentos_fallo=0, bloqueado_hasta=NULL WHERE id=%s",
            (hashed, user_id),
        )
        conn.commit()
        print(f"Contraseña actualizada para usuario '{username}'")
    else:
        cur.execute(
            """
            INSERT INTO usuarios (id, nombre_usuario, email, hash_contraseña, nombre_completo, activo, usuario_creacion)
            VALUES (uuid_generate_v4(), %s, %s, %s, %s, TRUE, %s)
            RETURNING id
            """,
            (username, f"{username}@clinica.local", hashed, "Administrador", "system"),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.execute("SELECT id FROM roles WHERE nombre_rol = %s", ("Administrador",))
        role = cur.fetchone()
        if role:
            role_id = role[0]
            cur.execute(
                "INSERT INTO usuarios_roles (usuario_id, rol_id, usuario_asignacion) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (new_id, role_id, "system"),
            )
            conn.commit()
        print(f"Usuario '{username}' creado y contraseña definida")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
