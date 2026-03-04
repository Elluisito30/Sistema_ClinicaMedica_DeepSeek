import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db_connection import execute_query
from utils.auth import hash_password, check_permission
from utils.helpers import format_datetime
import logging

logger = logging.getLogger(__name__)

def show_usuarios():
    """Módulo de gestión de usuarios, roles y permisos"""
    st.title("👥 Gestión de Usuarios")
    
    # Tabs para diferentes secciones
    tab1, tab2, tab3 = st.tabs(["👤 Usuarios", "🎭 Roles", "🔑 Permisos"])
    
    with tab1:
        show_gestion_usuarios()
    
    with tab2:
        show_gestion_roles()
    
    with tab3:
        show_gestion_permisos()

def show_gestion_usuarios():
    """CRUD de usuarios"""
    st.header("Usuarios del Sistema")
    
    if not check_permission('gestionar_usuarios'):
        st.error("No tiene permisos para gestionar usuarios")
        return
    
    # Botón para nuevo usuario
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("➕ Nuevo Usuario", use_container_width=True):
            st.session_state.show_new_user_form = True
    
    # Formulario de nuevo usuario
    if st.session_state.get('show_new_user_form', False):
        with st.form("form_nuevo_usuario"):
            st.subheader("Registrar Nuevo Usuario")
            
            col1, col2 = st.columns(2)
            with col1:
                nombre_usuario = st.text_input("Nombre de Usuario*", max_chars=50)
                email = st.text_input("Email*", max_chars=100)
                password = st.text_input("Contraseña*", type="password")
            
            with col2:
                nombre_completo = st.text_input("Nombre Completo*", max_chars=150)
                tipo_usuario = st.selectbox(
                    "Tipo de Usuario*",
                    options=["medico", "paciente", "recepcionista", "administrador"]
                )
                confirm_password = st.text_input("Confirmar Contraseña*", type="password")
            
            # Campos específicos según tipo
            if tipo_usuario == "medico":
                col1, col2 = st.columns(2)
                with col1:
                    especialidades = get_especialidades_activas()
                    id_especialidad = st.selectbox(
                        "Especialidad*",
                        options=especialidades['id'].tolist() if not especialidades.empty else [],
                        format_func=lambda x: especialidades[especialidades['id'] == x]['nombre'].iloc[0]
                    )
                with col2:
                    numero_colegiado = st.text_input("Número de Colegiado*", max_chars=50)
            
            elif tipo_usuario == "paciente":
                col1, col2 = st.columns(2)
                with col1:
                    fecha_nacimiento = st.date_input("Fecha de Nacimiento*")
                with col2:
                    telefono = st.text_input("Teléfono", max_chars=20)
                direccion = st.text_input("Dirección", max_chars=200)
            
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                submit = st.form_submit_button("💾 Guardar", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submit:
                if not all([nombre_usuario, email, password, nombre_completo, confirm_password]):
                    st.error("Todos los campos marcados con * son obligatorios")
                elif password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                else:
                    crear_usuario(
                        nombre_usuario, email, password, nombre_completo,
                        tipo_usuario, locals()
                    )
            
            if cancel:
                st.session_state.show_new_user_form = False
                st.rerun()
    
    st.divider()
    
    # Listado de usuarios
    st.subheader("Listado de Usuarios")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_activo = st.selectbox(
            "Estado",
            options=["todos", "activos", "inactivos"],
            format_func=lambda x: {"todos": "Todos", "activos": "Activos", "inactivos": "Inactivos"}[x]
        )
    with col2:
        filtro_tipo = st.selectbox(
            "Tipo de Usuario",
            options=["todos", "administrador", "medico", "recepcionista", "paciente"]
        )
    with col3:
        busqueda = st.text_input("🔍 Buscar", placeholder="Nombre o email...")
    
    # Obtener usuarios
    usuarios = get_usuarios(filtro_activo, filtro_tipo, busqueda)
    
    if usuarios:
        for usuario in usuarios:
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1.5, 1, 1, 1])
                
                with col1:
                    st.write(f"**{usuario['nombre_completo']}**")
                with col2:
                    st.write(usuario['email'])
                with col3:
                    st.write(usuario['roles'] or "Sin rol")
                with col4:
                    estado = "✅ Activo" if usuario['activo'] else "❌ Inactivo"
                    st.write(estado)
                with col5:
                    if st.button("✏️", key=f"edit_user_{usuario['id']}", help="Editar"):
                        st.session_state[f"editing_user_{usuario['id']}"] = True
                with col6:
                    if st.button("🔒", key=f"reset_pass_{usuario['id']}", help="Resetear contraseña"):
                        resetear_password(usuario['id'])
                
                # Formulario de edición
                if st.session_state.get(f"editing_user_{usuario['id']}", False):
                    with st.form(key=f"edit_user_form_{usuario['id']}"):
                        st.write(f"**Editando: {usuario['nombre_completo']}**")
                        
                        new_nombre = st.text_input("Nombre Completo", value=usuario['nombre_completo'])
                        new_email = st.text_input("Email", value=usuario['email'])
                        new_activo = st.checkbox("Usuario Activo", value=usuario['activo'])
                        
                        # Asignación de roles
                        roles_disponibles = get_roles()
                        roles_actuales = get_roles_usuario(usuario['id'])
                        
                        selected_roles = st.multiselect(
                            "Roles",
                            options=roles_disponibles['id'].tolist() if not roles_disponibles.empty else [],
                            default=roles_actuales['id'].tolist() if not roles_actuales.empty else [],
                            format_func=lambda x: roles_disponibles[roles_disponibles['id'] == x]['nombre'].iloc[0]
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Guardar"):
                                actualizar_usuario(usuario['id'], new_nombre, new_email, new_activo, selected_roles)
                        with col2:
                            if st.form_submit_button("❌ Cancelar"):
                                del st.session_state[f"editing_user_{usuario['id']}"]
                                st.rerun()
                
                st.divider()
    else:
        st.info("No se encontraron usuarios con los filtros seleccionados")

def crear_usuario(username, email, password, nombre_completo, tipo_usuario, extra_data):
    """Crea un nuevo usuario en el sistema"""
    try:
        # Insertar en tabla usuarios
        query_usuario = """
            INSERT INTO usuarios 
            (nombre_usuario, email, hash_contraseña, nombre_completo, usuario_creacion)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        hashed_pw = hash_password(password)
        result = execute_query(
            query_usuario,
            (username, email, hashed_pw, nombre_completo, st.session_state.username),
            fetch_one=True,
            commit=True
        )
        
        if not result:
            st.error("Error al crear el usuario")
            return
        
        user_id = result['id']
        
        # Asignar rol según tipo
        rol_map = {
            "administrador": "Administrador",
            "medico": "Médico",
            "recepcionista": "Recepcionista",
            "paciente": "Paciente"
        }
        
        query_rol = """
            INSERT INTO usuarios_roles (usuario_id, rol_id, usuario_asignacion)
            SELECT %s, id, %s FROM roles WHERE nombre_rol = %s
        """
        execute_query(query_rol, (user_id, st.session_state.username, rol_map[tipo_usuario]), commit=True)
        
        # Insertar datos específicos según tipo
        if tipo_usuario == "medico":
            query_medico = """
                INSERT INTO medicos (id, id_especialidad, numero_colegiado, usuario_creacion)
                VALUES (%s, %s, %s, %s)
            """
            execute_query(
                query_medico,
                (user_id, extra_data['id_especialidad'], extra_data['numero_colegiado'], st.session_state.username),
                commit=True
            )
        
        elif tipo_usuario == "paciente":
            query_paciente = """
                INSERT INTO pacientes (id, fecha_nacimiento, direccion, telefono, usuario_creacion)
                VALUES (%s, %s, %s, %s, %s)
            """
            execute_query(
                query_paciente,
                (user_id, extra_data['fecha_nacimiento'], extra_data.get('direccion', ''),
                 extra_data.get('telefono', ''), st.session_state.username),
                commit=True
            )
        
        st.success("Usuario creado exitosamente")
        st.session_state.show_new_user_form = False
        st.rerun()
        
    except Exception as e:
        if "unique" in str(e).lower():
            if "nombre_usuario" in str(e):
                st.error("El nombre de usuario ya está en uso")
            elif "email" in str(e):
                st.error("El email ya está registrado")
            else:
                st.error("Ya existe un usuario con esos datos")
        else:
            st.error(f"Error al crear el usuario: {str(e)}")

def get_usuarios(filtro_activo, filtro_tipo, busqueda):
    """Obtiene lista de usuarios con filtros"""
    condiciones = []
    params = []
    
    query_base = """
        SELECT 
            u.id,
            u.nombre_usuario,
            u.email,
            u.nombre_completo,
            u.activo,
            u.fecha_ultimo_acceso,
            u.intentos_fallo,
            u.bloqueado_hasta,
            STRING_AGG(DISTINCT r.nombre_rol, ', ') as roles
        FROM usuarios u
        LEFT JOIN usuarios_roles ur ON u.id = ur.usuario_id
        LEFT JOIN roles r ON ur.rol_id = r.id
        WHERE 1=1
    """
    
    if filtro_activo != "todos":
        condiciones.append("u.activo = %s")
        params.append(filtro_activo == "activos")
    
    if filtro_tipo != "todos":
        condiciones.append("EXISTS (SELECT 1 FROM usuarios_roles ur2 JOIN roles r2 ON ur2.rol_id = r2.id WHERE ur2.usuario_id = u.id AND LOWER(r2.nombre_rol) = %s)")
        params.append(filtro_tipo)
    
    if busqueda:
        condiciones.append("(u.nombre_completo ILIKE %s OR u.email ILIKE %s OR u.nombre_usuario ILIKE %s)")
        params.extend([f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"])
    
    if condiciones:
        query_base += " AND " + " AND ".join(condiciones)
    
    query_base += " GROUP BY u.id ORDER BY u.nombre_completo"
    
    return execute_query(query_base, tuple(params) if params else None, fetch_all=True)

def get_roles():
    """Obtiene lista de roles disponibles"""
    query = "SELECT id, nombre_rol as nombre, descripcion FROM roles ORDER BY nombre_rol"
    result = execute_query(query, fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def get_roles_usuario(user_id):
    """Obtiene roles asignados a un usuario"""
    query = """
        SELECT r.id, r.nombre_rol as nombre
        FROM roles r
        JOIN usuarios_roles ur ON r.id = ur.rol_id
        WHERE ur.usuario_id = %s
    """
    result = execute_query(query, (user_id,), fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def actualizar_usuario(user_id, nombre_completo, email, activo, roles):
    """Actualiza datos de usuario"""
    try:
        # Actualizar datos básicos
        query_update = """
            UPDATE usuarios 
            SET nombre_completo = %s,
                email = %s,
                activo = %s,
                fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id = %s
        """
        execute_query(
            query_update,
            (nombre_completo, email, activo, st.session_state.username, user_id),
            commit=True
        )
        
        # Actualizar roles
        # Eliminar roles actuales
        execute_query("DELETE FROM usuarios_roles WHERE usuario_id = %s", (user_id,), commit=True)
        
        # Asignar nuevos roles
        for rol_id in roles:
            query_rol = """
                INSERT INTO usuarios_roles (usuario_id, rol_id, usuario_asignacion)
                VALUES (%s, %s, %s)
            """
            execute_query(query_rol, (user_id, rol_id, st.session_state.username), commit=True)
        
        st.success("Usuario actualizado exitosamente")
        del st.session_state[f"editing_user_{user_id}"]
        st.rerun()
        
    except Exception as e:
        st.error(f"Error al actualizar usuario: {str(e)}")

def resetear_password(user_id):
    """Resetea la contraseña de un usuario"""
    try:
        # Generar contraseña temporal
        temp_password = "Temp123456!"
        hashed_pw = hash_password(temp_password)
        
        query = """
            UPDATE usuarios 
            SET hash_contraseña = %s,
                requiere_cambio_contraseña = true,
                fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id = %s
        """
        execute_query(query, (hashed_pw, st.session_state.username, user_id), commit=True)
        
        st.success(f"Contraseña reseteada. Contraseña temporal: {temp_password}")
        
    except Exception as e:
        st.error(f"Error al resetear contraseña: {str(e)}")

def get_especialidades_activas():
    """Obtiene especialidades activas para select"""
    query = "SELECT id, nombre_especialidad as nombre FROM especialidades WHERE activo = true ORDER BY nombre_especialidad"
    result = execute_query(query, fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def show_gestion_roles():
    """Gestión de roles"""
    st.header("Gestión de Roles")
    
    if not check_permission('gestionar_roles'):
        st.error("No tiene permisos para gestionar roles")
        return
    
    # Formulario para nuevo rol
    with st.expander("➕ Nuevo Rol", expanded=False):
        with st.form("form_nuevo_rol"):
            nombre_rol = st.text_input("Nombre del Rol*", max_chars=50)
            descripcion = st.text_area("Descripción", max_chars=200)
            
            # Selección de permisos
            permisos = get_permisos_agrupados()
            st.write("**Permisos del Rol:**")
            
            selected_permisos = []
            for modulo, perms in permisos.items():
                st.write(f"**{modulo}**")
                cols = st.columns(3)
                for i, perm in enumerate(perms):
                    with cols[i % 3]:
                        if st.checkbox(perm['descripcion'], key=f"perm_{perm['id']}"):
                            selected_permisos.append(perm['id'])
                st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("💾 Guardar Rol", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submit:
                if not nombre_rol:
                    st.error("El nombre del rol es obligatorio")
                else:
                    crear_rol(nombre_rol, descripcion, selected_permisos)
    
    # Listado de roles
    st.subheader("Roles Existentes")
    roles = get_roles_detalle()
    
    if not roles.empty:
        for _, rol in roles.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.write(f"**{rol['nombre']}**")
                with col2:
                    st.write(rol['descripcion'] or "—")
                with col3:
                    if st.button("✏️ Editar", key=f"edit_rol_{rol['id']}"):
                        st.session_state[f"editing_rol_{rol['id']}"] = True
                
                if st.session_state.get(f"editing_rol_{rol['id']}", False):
                    with st.form(key=f"edit_rol_form_{rol['id']}"):
                        st.write(f"**Editando: {rol['nombre']}**")
                        new_desc = st.text_input("Descripción", value=rol['descripcion'] or "")
                        
                        # Permisos actuales del rol
                        permisos_actuales = get_permisos_rol(rol['id'])
                        permisos_actuales_ids = [p['id'] for p in permisos_actuales] if permisos_actuales else []
                        
                        st.write("**Permisos:**")
                        new_permisos = []
                        for modulo, perms in permisos.items():
                            st.write(f"**{modulo}**")
                            cols = st.columns(3)
                            for i, perm in enumerate(perms):
                                with cols[i % 3]:
                                    checked = perm['id'] in permisos_actuales_ids
                                    if st.checkbox(perm['descripcion'], value=checked, key=f"edit_perm_{rol['id']}_{perm['id']}"):
                                        new_permisos.append(perm['id'])
                            st.divider()
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Guardar"):
                                actualizar_rol(rol['id'], new_desc, new_permisos)
                        with col2:
                            if st.form_submit_button("❌ Cancelar"):
                                del st.session_state[f"editing_rol_{rol['id']}"]
                                st.rerun()
                
                st.divider()
    else:
        st.info("No hay roles registrados")

def get_permisos_agrupados():
    """Obtiene permisos agrupados por módulo"""
    query = "SELECT id, nombre_permiso, descripcion, modulo FROM permisos ORDER BY modulo, nombre_permiso"
    result = execute_query(query, fetch_all=True)
    
    if not result:
        return {}
    
    permisos = {}
    for perm in result:
        modulo = perm['modulo'].capitalize()
        if modulo not in permisos:
            permisos[modulo] = []
        permisos[modulo].append({
            'id': perm['id'],
            'nombre': perm['nombre_permiso'],
            'descripcion': perm['descripcion']
        })
    
    return permisos

def get_permisos_rol(rol_id):
    """Obtiene permisos de un rol específico"""
    query = """
        SELECT p.id, p.nombre_permiso, p.descripcion
        FROM permisos p
        JOIN roles_permisos rp ON p.id = rp.permiso_id
        WHERE rp.rol_id = %s
    """
    return execute_query(query, (rol_id,), fetch_all=True)

def crear_rol(nombre, descripcion, permisos):
    """Crea un nuevo rol con sus permisos"""
    try:
        # Insertar rol
        query_rol = """
            INSERT INTO roles (nombre_rol, descripcion, usuario_creacion)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        result = execute_query(
            query_rol,
            (nombre, descripcion, st.session_state.username),
            fetch_one=True,
            commit=True
        )
        
        if not result:
            st.error("Error al crear el rol")
            return
        
        rol_id = result['id']
        
        # Asignar permisos
        for permiso_id in permisos:
            query_permiso = """
                INSERT INTO roles_permisos (rol_id, permiso_id, usuario_asignacion)
                VALUES (%s, %s, %s)
            """
            execute_query(query_permiso, (rol_id, permiso_id, st.session_state.username), commit=True)
        
        st.success("Rol creado exitosamente")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error al crear el rol: {str(e)}")

def actualizar_rol(rol_id, descripcion, permisos):
    """Actualiza un rol y sus permisos"""
    try:
        # Actualizar descripción
        query_update = """
            UPDATE roles 
            SET descripcion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id = %s
        """
        execute_query(query_update, (descripcion, st.session_state.username, rol_id), commit=True)
        
        # Eliminar permisos actuales
        execute_query("DELETE FROM roles_permisos WHERE rol_id = %s", (rol_id,), commit=True)
        
        # Asignar nuevos permisos
        for permiso_id in permisos:
            query_permiso = """
                INSERT INTO roles_permisos (rol_id, permiso_id, usuario_asignacion)
                VALUES (%s, %s, %s)
            """
            execute_query(query_permiso, (rol_id, permiso_id, st.session_state.username), commit=True)
        
        st.success("Rol actualizado exitosamente")
        del st.session_state[f"editing_rol_{rol_id}"]
        st.rerun()
        
    except Exception as e:
        st.error(f"Error al actualizar el rol: {str(e)}")

def get_roles_detalle():
    """Obtiene lista detallada de roles"""
    query = """
        SELECT 
            r.id,
            r.nombre_rol as nombre,
            r.descripcion,
            COUNT(DISTINCT ur.usuario_id) as total_usuarios,
            COUNT(DISTINCT rp.permiso_id) as total_permisos
        FROM roles r
        LEFT JOIN usuarios_roles ur ON r.id = ur.rol_id
        LEFT JOIN roles_permisos rp ON r.id = rp.rol_id
        GROUP BY r.id, r.nombre_rol, r.descripcion
        ORDER BY r.nombre_rol
    """
    result = execute_query(query, fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def show_gestion_permisos():
    """Vista de permisos del sistema"""
    st.header("Permisos del Sistema")
    
    if not check_permission('gestionar_roles'):
        st.error("No tiene permisos para ver esta sección")
        return
    
    permisos = get_permisos_agrupados()
    
    for modulo, perms in permisos.items():
        with st.expander(f"📁 {modulo}", expanded=False):
            df_permisos = pd.DataFrame(perms)
            if not df_permisos.empty:
                st.dataframe(
                    df_permisos[['nombre', 'descripcion']],
                    column_config={
                        "nombre": "Permiso",
                        "descripcion": "Descripción"
                    },
                    use_container_width=True,
                    hide_index=True
                )