-- ============================================================
-- SEED SEGURO PARA pgAdmin - Con manejo de errores por bloque
-- ============================================================

-- ROLES
DO $$ BEGIN
  INSERT INTO roles (nombre_rol, descripcion, usuario_creacion)
  SELECT 'Administrador', 'Acceso total', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM roles WHERE nombre_rol = 'Administrador');
  RAISE NOTICE 'OK: Rol Administrador';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP roles Administrador: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles (nombre_rol, descripcion, usuario_creacion)
  SELECT 'Médico', 'Atiende pacientes y gestiona historias clínicas', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM roles WHERE nombre_rol = 'Médico');
  RAISE NOTICE 'OK: Rol Médico';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP roles Médico: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles (nombre_rol, descripcion, usuario_creacion)
  SELECT 'Recepcionista', 'Gestiona citas y pacientes', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM roles WHERE nombre_rol = 'Recepcionista');
  RAISE NOTICE 'OK: Rol Recepcionista';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP roles Recepcionista: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles (nombre_rol, descripcion, usuario_creacion)
  SELECT 'Paciente', 'Acceso limitado', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM roles WHERE nombre_rol = 'Paciente');
  RAISE NOTICE 'OK: Rol Paciente';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP roles Paciente: %', SQLERRM; END $$;

-- PERMISOS
DO $$ BEGIN
  INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion)
  SELECT 'ver_dashboard', 'Ver panel principal', 'Dashboard', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'ver_dashboard');
  RAISE NOTICE 'OK: Permiso ver_dashboard';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP permiso ver_dashboard: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion)
  SELECT 'ver_citas', 'Ver citas', 'Procesos', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'ver_citas');
  RAISE NOTICE 'OK: Permiso ver_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP permiso ver_citas: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion)
  SELECT 'crear_citas', 'Crear citas', 'Procesos', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'crear_citas');
  RAISE NOTICE 'OK: Permiso crear_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP permiso crear_citas: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion)
  SELECT 'editar_citas', 'Editar/confirmar/cancelar citas', 'Procesos', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'editar_citas');
  RAISE NOTICE 'OK: Permiso editar_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP permiso editar_citas: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion)
  SELECT 'atender_citas', 'Atender y registrar atenciones', 'Procesos', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'atender_citas');
  RAISE NOTICE 'OK: Permiso atender_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP permiso atender_citas: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion)
  SELECT 'generar_reportes', 'Acceder a reportes', 'Reportes', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'generar_reportes');
  RAISE NOTICE 'OK: Permiso generar_reportes';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP permiso generar_reportes: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion)
  SELECT 'gestionar_mantenedores', 'Gestionar catálogos básicos', 'Mantenedores', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'gestionar_mantenedores');
  RAISE NOTICE 'OK: Permiso gestionar_mantenedores';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP permiso gestionar_mantenedores: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion)
  SELECT 'gestionar_usuarios', 'Gestionar usuarios', 'Usuarios', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'gestionar_usuarios');
  RAISE NOTICE 'OK: Permiso gestionar_usuarios';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP permiso gestionar_usuarios: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion)
  SELECT 'gestionar_roles', 'Gestionar roles y permisos', 'Usuarios', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'gestionar_roles');
  RAISE NOTICE 'OK: Permiso gestionar_roles';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP permiso gestionar_roles: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion)
  SELECT 'gestionar_backups', 'Gestionar backups', 'Backup', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM permisos WHERE nombre_permiso = 'gestionar_backups');
  RAISE NOTICE 'OK: Permiso gestionar_backups';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP permiso gestionar_backups: %', SQLERRM; END $$;

-- ROLES_PERMISOS - ADMINISTRADOR (todos los permisos)
DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Administrador' AND p.nombre_permiso = 'ver_dashboard'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Administrador -> ver_dashboard';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Administrador' AND p.nombre_permiso = 'ver_citas'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Administrador -> ver_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Administrador' AND p.nombre_permiso = 'crear_citas'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Administrador -> crear_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Administrador' AND p.nombre_permiso = 'editar_citas'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Administrador -> editar_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Administrador' AND p.nombre_permiso = 'atender_citas'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Administrador -> atender_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Administrador' AND p.nombre_permiso = 'generar_reportes'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Administrador -> generar_reportes';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Administrador' AND p.nombre_permiso = 'gestionar_mantenedores'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Administrador -> gestionar_mantenedores';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Administrador' AND p.nombre_permiso = 'gestionar_usuarios'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Administrador -> gestionar_usuarios';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Administrador' AND p.nombre_permiso = 'gestionar_roles'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Administrador -> gestionar_roles';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Administrador' AND p.nombre_permiso = 'gestionar_backups'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Administrador -> gestionar_backups';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

-- ROLES_PERMISOS - MÉDICO (separados para evitar cross join con IN)
DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Médico' AND p.nombre_permiso = 'ver_dashboard'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Médico -> ver_dashboard';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Médico' AND p.nombre_permiso = 'ver_citas'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Médico -> ver_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Médico' AND p.nombre_permiso = 'atender_citas'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Médico -> atender_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Médico' AND p.nombre_permiso = 'generar_reportes'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Médico -> generar_reportes';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

-- ROLES_PERMISOS - RECEPCIONISTA
DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Recepcionista' AND p.nombre_permiso = 'ver_citas'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Recepcionista -> ver_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Recepcionista' AND p.nombre_permiso = 'crear_citas'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Recepcionista -> crear_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO roles_permisos (rol_id, permiso_id)
  SELECT r.id, p.id FROM roles r, permisos p
  WHERE r.nombre_rol = 'Recepcionista' AND p.nombre_permiso = 'editar_citas'
  AND NOT EXISTS (SELECT 1 FROM roles_permisos rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id);
  RAISE NOTICE 'OK: Recepcionista -> editar_citas';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP: %', SQLERRM; END $$;

-- USUARIOS
DO $$ BEGIN
  INSERT INTO usuarios (nombre_usuario, email, hash_contraseña, nombre_completo, activo, usuario_creacion)
  SELECT 'drhouse', 'dr.house@example.com', '$2b$12$invalidinvalidinvalidinvalidinvalidinv', 'Gregory House', true, 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE nombre_usuario = 'drhouse' OR email = 'dr.house@example.com');
  RAISE NOTICE 'OK: Usuario drhouse';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP usuario drhouse: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO usuarios (nombre_usuario, email, hash_contraseña, nombre_completo, activo, usuario_creacion)
  SELECT 'jperez', 'juan.perez@example.com', '$2b$12$invalidinvalidinvalidinvalidinvalidinv', 'Juan Pérez', true, 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE nombre_usuario = 'jperez' OR email = 'juan.perez@example.com');
  RAISE NOTICE 'OK: Usuario jperez';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP usuario jperez: %', SQLERRM; END $$;

-- USUARIOS_ROLES
DO $$ BEGIN
  INSERT INTO usuarios_roles (usuario_id, rol_id)
  SELECT u.id, r.id FROM usuarios u, roles r
  WHERE u.nombre_usuario = 'drhouse' AND r.nombre_rol = 'Médico'
  AND NOT EXISTS (SELECT 1 FROM usuarios_roles ur WHERE ur.usuario_id = u.id AND ur.rol_id = r.id);
  RAISE NOTICE 'OK: drhouse -> Médico';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP usuarios_roles drhouse: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO usuarios_roles (usuario_id, rol_id)
  SELECT u.id, r.id FROM usuarios u, roles r
  WHERE u.nombre_usuario = 'jperez' AND r.nombre_rol = 'Paciente'
  AND NOT EXISTS (SELECT 1 FROM usuarios_roles ur WHERE ur.usuario_id = u.id AND ur.rol_id = r.id);
  RAISE NOTICE 'OK: jperez -> Paciente';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP usuarios_roles jperez: %', SQLERRM; END $$;

-- ESPECIALIDADES
DO $$ BEGIN
  INSERT INTO especialidades (nombre_especialidad, descripcion, usuario_creacion)
  SELECT 'Cardiología', 'Especialidad de cardiología', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM especialidades WHERE nombre_especialidad = 'Cardiología');
  RAISE NOTICE 'OK: Especialidad Cardiología';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP especialidades: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO especialidades (nombre_especialidad, descripcion, usuario_creacion)
  SELECT 'Medicina Interna', 'Especialidad de medicina interna', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM especialidades WHERE nombre_especialidad = 'Medicina Interna');
  RAISE NOTICE 'OK: Especialidad Medicina Interna';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP especialidades: %', SQLERRM; END $$;

-- MEDICOS
DO $$ BEGIN
  INSERT INTO medicos (id, id_especialidad, numero_colegiado, usuario_creacion)
  SELECT u.id, e.id, 'MED-0001', 'seed_sql'
  FROM usuarios u, especialidades e
  WHERE u.nombre_usuario = 'drhouse' AND e.nombre_especialidad = 'Cardiología'
  AND NOT EXISTS (SELECT 1 FROM medicos m WHERE m.id = u.id);
  RAISE NOTICE 'OK: Médico drhouse';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP medicos: %', SQLERRM; END $$;

-- PACIENTES
DO $$ BEGIN
  INSERT INTO pacientes (id, fecha_nacimiento, direccion, telefono, usuario_creacion)
  SELECT u.id, DATE '1990-05-20', 'Av. Siempre Viva 742', '987654321', 'seed_sql'
  FROM usuarios u
  WHERE u.nombre_usuario = 'jperez'
  AND NOT EXISTS (SELECT 1 FROM pacientes p WHERE p.id = u.id);
  RAISE NOTICE 'OK: Paciente jperez';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP pacientes: %', SQLERRM; END $$;

-- CONSULTORIOS
DO $$ BEGIN
  INSERT INTO consultorios (nombre, ubicacion, usuario_creacion)
  SELECT 'Consultorio 1', 'Primer piso', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM consultorios WHERE nombre = 'Consultorio 1');
  RAISE NOTICE 'OK: Consultorio 1';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP consultorios: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO consultorios (nombre, ubicacion, usuario_creacion)
  SELECT 'Consultorio 2', 'Segundo piso', 'seed_sql'
  WHERE NOT EXISTS (SELECT 1 FROM consultorios WHERE nombre = 'Consultorio 2');
  RAISE NOTICE 'OK: Consultorio 2';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP consultorios: %', SQLERRM; END $$;

-- CITAS
DO $$ BEGIN
  INSERT INTO citas (id_paciente, id_medico, id_consultorio, fecha_hora_cita, motivo_consulta, estado, usuario_creacion)
  SELECT p.id, m.id, c.id,
    (CURRENT_DATE + INTERVAL '1 day')::timestamp + INTERVAL '9 hour',
    'Chequeo de rutina', 'programada', 'seed_sql'
  FROM pacientes p, medicos m, consultorios c
  WHERE p.id = (SELECT id FROM usuarios WHERE nombre_usuario = 'jperez')
    AND m.id = (SELECT id FROM usuarios WHERE nombre_usuario = 'drhouse')
    AND c.nombre = 'Consultorio 1'
    AND NOT EXISTS (
      SELECT 1 FROM citas cc
      WHERE cc.id_paciente = p.id AND cc.id_medico = m.id
        AND cc.fecha_hora_cita = (CURRENT_DATE + INTERVAL '1 day')::timestamp + INTERVAL '9 hour'
    );
  RAISE NOTICE 'OK: Cita programada';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP cita programada: %', SQLERRM; END $$;

DO $$ BEGIN
  INSERT INTO citas (id_paciente, id_medico, id_consultorio, fecha_hora_cita, motivo_consulta, estado, usuario_creacion)
  SELECT p.id, m.id, c.id,
    CURRENT_DATE::timestamp + INTERVAL '10 hour',
    'Dolor torácico', 'completada', 'seed_sql'
  FROM pacientes p, medicos m, consultorios c
  WHERE p.id = (SELECT id FROM usuarios WHERE nombre_usuario = 'jperez')
    AND m.id = (SELECT id FROM usuarios WHERE nombre_usuario = 'drhouse')
    AND c.nombre = 'Consultorio 2'
    AND NOT EXISTS (
      SELECT 1 FROM citas cc
      WHERE cc.id_paciente = p.id AND cc.id_medico = m.id
        AND cc.fecha_hora_cita = CURRENT_DATE::timestamp + INTERVAL '10 hour'
    );
  RAISE NOTICE 'OK: Cita completada';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP cita completada: %', SQLERRM; END $$;

-- HISTORIAL MÉDICO
DO $$ BEGIN
  INSERT INTO historial_medico (id_paciente, id_medico, id_cita, diagnostico, tratamiento, receta, notas_evolucion, signos_vitales, usuario_creacion)
  SELECT cc.id_paciente, cc.id_medico, cc.id,
    'Angina estable', 'Nitroglicerina sublingual', 'Nitroglicerina 0.4mg SL prn dolor',
    'Paciente estable, control en 2 semanas',
    '{"presion":"130/85","temperatura":36.7,"peso":78.5,"altura":1.75}', 'seed_sql'
  FROM citas cc
  WHERE cc.id_paciente = (SELECT id FROM usuarios WHERE nombre_usuario = 'jperez')
    AND cc.id_medico = (SELECT id FROM usuarios WHERE nombre_usuario = 'drhouse')
    AND cc.fecha_hora_cita = CURRENT_DATE::timestamp + INTERVAL '10 hour'
    AND NOT EXISTS (SELECT 1 FROM historial_medico hm WHERE hm.id_cita = cc.id);
  RAISE NOTICE 'OK: Historial médico';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP historial_medico: %', SQLERRM; END $$;

-- FACTURAS
DO $$ BEGIN
  INSERT INTO facturas (id_paciente, id_cita, numero_factura, fecha_emision, monto_total, metodo_pago, estado_pago, usuario_creacion)
  SELECT cc.id_paciente, cc.id, 'SEED-' || cc.id::text, CURRENT_DATE, 150.00, 'efectivo', 'pagado', 'seed_sql'
  FROM citas cc
  WHERE cc.id_paciente = (SELECT id FROM usuarios WHERE nombre_usuario = 'jperez')
    AND cc.id_medico = (SELECT id FROM usuarios WHERE nombre_usuario = 'drhouse')
    AND cc.fecha_hora_cita = CURRENT_DATE::timestamp + INTERVAL '10 hour'
    AND NOT EXISTS (SELECT 1 FROM facturas f WHERE f.id_cita = cc.id);
  RAISE NOTICE 'OK: Factura';
EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'SKIP facturas: %', SQLERRM; END $$;

-- FIN DEL SEED