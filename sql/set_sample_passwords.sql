CREATE EXTENSION IF NOT EXISTS pgcrypto;

UPDATE usuarios
SET hash_contraseña = crypt('drhouse123', gen_salt('bf')), requiere_cambio_contraseña = false
WHERE nombre_usuario = 'drhouse';

UPDATE usuarios
SET hash_contraseña = crypt('jperez123', gen_salt('bf')), requiere_cambio_contraseña = false
WHERE nombre_usuario = 'jperez';

UPDATE usuarios
SET hash_contraseña = crypt('admin123', gen_salt('bf')), requiere_cambio_contraseña = false
WHERE nombre_usuario = 'admin';