-- Otorgar permisos mínimos al rol Paciente para operar en Procesos

-- Crear permisos si no existen
INSERT INTO permisos (nombre_permiso, descripcion, modulo)
SELECT 'ver_citas', 'Ver citas', 'Procesos'
WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'ver_citas');

INSERT INTO permisos (nombre_permiso, descripcion, modulo)
SELECT 'crear_citas', 'Crear citas', 'Procesos'
WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'crear_citas');

-- (Opcional) Mostrar Dashboard a Paciente
INSERT INTO permisos (nombre_permiso, descripcion, modulo)
SELECT 'ver_dashboard', 'Ver panel principal', 'Dashboard'
WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'ver_dashboard');

-- Asignar a rol Paciente de forma idempotente
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM roles r, permisos p
WHERE r.nombre_rol = 'Paciente' AND p.nombre_permiso = 'ver_citas'
AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);

INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM roles r, permisos p
WHERE r.nombre_rol = 'Paciente' AND p.nombre_permiso = 'crear_citas'
AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);

-- (Opcional) Permitir ver Dashboard
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM roles r, permisos p
WHERE r.nombre_rol = 'Paciente' AND p.nombre_permiso = 'ver_dashboard'
AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
