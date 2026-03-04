INSERT INTO permisos (nombre_permiso, descripcion, modulo)
SELECT 'ver_citas', 'Ver citas', 'Procesos'
WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'ver_citas');

INSERT INTO permisos (nombre_permiso, descripcion, modulo)
SELECT 'crear_citas', 'Crear citas', 'Procesos'
WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'crear_citas');

INSERT INTO permisos (nombre_permiso, descripcion, modulo)
SELECT 'editar_citas', 'Editar/confirmar/cancelar citas', 'Procesos'
WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'editar_citas');

INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM roles r, permisos p
WHERE r.nombre_rol = 'Recepcionista' AND p.nombre_permiso = 'ver_citas'
AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);

INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM roles r, permisos p
WHERE r.nombre_rol = 'Recepcionista' AND p.nombre_permiso = 'crear_citas'
AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);

INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM roles r, permisos p
WHERE r.nombre_rol = 'Recepcionista' AND p.nombre_permiso = 'editar_citas'
AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
