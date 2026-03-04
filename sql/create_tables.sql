-- Base de datos: bd_sistemaclinica
-- Crear la base de datos (ejecutar separadamente)
-- CREATE DATABASE bd_sistemaclinica;

-- Extensión para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLAS DE SEGURIDAD Y USUARIOS
-- =====================================================

-- Tabla de usuarios
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hash_contraseña TEXT NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_ultimo_acceso TIMESTAMP,
    intentos_fallo INTEGER DEFAULT 0,
    bloqueado_hasta TIMESTAMP,
    requiere_cambio_contraseña BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50),
    fecha_modificacion TIMESTAMP,
    usuario_modificacion VARCHAR(50)
);

-- Tabla de roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50)
);

-- Tabla de permisos
CREATE TABLE permisos (
    id SERIAL PRIMARY KEY,
    nombre_permiso VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    modulo VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50),
    fecha_modificacion TIMESTAMP,
    usuario_modificacion VARCHAR(50)
);

-- Relación usuarios-roles
CREATE TABLE usuarios_roles (
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    rol_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_asignacion VARCHAR(50),
    PRIMARY KEY (usuario_id, rol_id)
);

-- Relación roles-permisos
CREATE TABLE roles_permisos (
    rol_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id INTEGER REFERENCES permisos(id) ON DELETE CASCADE,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (rol_id, permiso_id)
);

-- =====================================================
-- TABLAS DE MANTENEDORES
-- =====================================================

-- Especialidades médicas
CREATE TABLE especialidades (
    id SERIAL PRIMARY KEY,
    nombre_especialidad VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50),
    fecha_modificacion TIMESTAMP,
    usuario_modificacion VARCHAR(50)
);

-- Consultorios
CREATE TABLE consultorios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    ubicacion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50),
    fecha_modificacion TIMESTAMP,
    usuario_modificacion VARCHAR(50)
);

-- Médicos (extensión de usuarios)
CREATE TABLE medicos (
    id UUID PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
    id_especialidad INTEGER REFERENCES especialidades(id),
    numero_colegiado VARCHAR(50) UNIQUE NOT NULL,
    horario_atencion JSONB, -- Formato: {"lunes": ["09:00-13:00", "15:00-19:00"], ...}
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50),
    fecha_modificacion TIMESTAMP,
    usuario_modificacion VARCHAR(50)
);

-- Pacientes (extensión de usuarios)
CREATE TABLE pacientes (
    id UUID PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_nacimiento DATE NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    contacto_emergencia JSONB, -- {"nombre": "", "telefono": "", "relacion": ""}
    historial_resumen TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50),
    fecha_modificacion TIMESTAMP,
    usuario_modificacion VARCHAR(50)
);

-- =====================================================
-- TABLAS DE PROCESOS
-- =====================================================

-- Citas médicas
CREATE TABLE citas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_paciente UUID REFERENCES pacientes(id) ON DELETE CASCADE,
    id_medico UUID REFERENCES medicos(id) ON DELETE CASCADE,
    id_consultorio INTEGER REFERENCES consultorios(id),
    fecha_hora_cita TIMESTAMP NOT NULL,
    motivo_consulta TEXT,
    estado VARCHAR(20) DEFAULT 'programada',
    notas TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50),
    fecha_modificacion TIMESTAMP,
    usuario_modificacion VARCHAR(50),
    -- Restricción para evitar doble agendamiento del mismo médico
    UNIQUE(id_medico, fecha_hora_cita)
);

-- Historial médico
CREATE TABLE historial_medico (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_paciente UUID REFERENCES pacientes(id) ON DELETE CASCADE,
    id_medico UUID REFERENCES medicos(id),
    id_cita UUID REFERENCES citas(id),
    fecha_atencion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    diagnostico TEXT NOT NULL,
    tratamiento TEXT,
    receta TEXT,
    notas_evolucion TEXT,
    signos_vitales JSONB, -- {"presion": "120/80", "temperatura": 36.5, "peso": 70, "altura": 1.75}
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50)
);

-- Facturas
CREATE TABLE facturas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_paciente UUID REFERENCES pacientes(id),
    id_cita UUID REFERENCES citas(id),
    numero_factura VARCHAR(20) UNIQUE NOT NULL,
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    monto_total DECIMAL(10, 2) NOT NULL,
    metodo_pago VARCHAR(30),
    estado_pago VARCHAR(20) DEFAULT 'pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50),
    fecha_modificacion TIMESTAMP,
    usuario_modificacion VARCHAR(50)
);

-- =====================================================
-- TABLAS DE BACKUP
-- =====================================================

-- Registro de backups
CREATE TABLE registro_backups (
    id SERIAL PRIMARY KEY,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP,
    tipo VARCHAR(20) CHECK (tipo IN ('completo', 'incremental')),
    estado VARCHAR(20) CHECK (estado IN ('exitoso', 'fallido', 'en_progreso')),
    tamano_mb DECIMAL(10, 2),
    ruta_archivo TEXT,
    usuario_ejecutor VARCHAR(50),
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Insertar roles básicos
INSERT INTO roles (nombre_rol, descripcion, usuario_creacion) VALUES
('Administrador', 'Acceso total al sistema', 'system'),
('Médico', 'Acceso a citas, historial médico y reportes básicos', 'system'),
('Recepcionista', 'Gestión de citas y pacientes', 'system'),
('Paciente', 'Acceso a portal del paciente (citas propias, historial)', 'system');

-- Insertar permisos básicos
INSERT INTO permisos (nombre_permiso, descripcion, modulo, usuario_creacion) VALUES
('ver_dashboard', 'Ver dashboard principal', 'dashboard', 'system'),
('gestionar_usuarios', 'Crear, editar y eliminar usuarios', 'usuarios', 'system'),
('gestionar_roles', 'Gestionar roles y permisos', 'usuarios', 'system'),
('gestionar_mantenedores', 'Gestionar especialidades y consultorios', 'mantenedores', 'system'),
('ver_citas', 'Ver citas', 'procesos', 'system'),
('crear_citas', 'Agendar nuevas citas', 'procesos', 'system'),
('editar_citas', 'Modificar citas existentes', 'procesos', 'system'),
('atender_citas', 'Registrar atención médica', 'procesos', 'system'),
('ver_historial', 'Ver historial médico', 'procesos', 'system'),
('generar_reportes', 'Generar reportes', 'reportes', 'system'),
('gestionar_backups', 'Realizar y ver backups', 'backup', 'system');

-- Asignar permisos al rol Administrador (todos)
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT 1, id FROM permisos;
