import bcrypt
import streamlit as st
from datetime import datetime, timedelta
import os
from utils.db_connection import execute_query
import logging

logger = logging.getLogger(__name__)

def hash_password(password):
    """Genera hash de contraseña"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    """Verifica contraseña contra hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False

def authenticate_user(username, password):
    """
    Autentica un usuario y maneja intentos fallidos
    Retorna: (success, user_data, message)
    """
    # Buscar usuario
    query = """
        SELECT id, nombre_usuario, email, hash_contraseña, nombre_completo,
               activo, intentos_fallo, bloqueado_hasta, requiere_cambio_contraseña
        FROM usuarios 
        WHERE nombre_usuario = %s OR email = %s
    """
    user = execute_query(query, (username, username), fetch_one=True)
    
    if not user:
        return False, None, "Usuario no encontrado"
    
    # Verificar si está bloqueado
    if user['bloqueado_hasta']:
        bloqueado_hasta = user['bloqueado_hasta']
        if isinstance(bloqueado_hasta, str):
            bloqueado_hasta = datetime.fromisoformat(bloqueado_hasta)
        
        if bloqueado_hasta > datetime.now():
            tiempo_restante = bloqueado_hasta - datetime.now()
            minutos = int(tiempo_restante.total_seconds() / 60)
            return False, None, f"Usuario bloqueado. Intente nuevamente en {minutos} minutos"
        else:
            # Desbloquear automáticamente
            execute_query(
                "UPDATE usuarios SET bloqueado_hasta = NULL, intentos_fallo = 0 WHERE id = %s",
                (user['id'],),
                commit=True
            )
    
    # Verificar activo
    if not user['activo']:
        return False, None, "Usuario inactivo. Contacte al administrador"
    
    # Verificar contraseña
    if verify_password(password, user['hash_contraseña']):
        # Resetear intentos fallidos
        execute_query(
            "UPDATE usuarios SET intentos_fallo = 0, fecha_ultimo_acceso = %s WHERE id = %s",
            (datetime.now(), user['id']),
            commit=True
        )
        return True, user, "Autenticación exitosa"
    else:
        # Incrementar intentos fallidos
        max_intentos = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
        bloqueo_minutos = int(os.getenv('BLOCK_TIME_MINUTES', 15))
        
        nuevos_intentos = user['intentos_fallo'] + 1
        
        if nuevos_intentos >= max_intentos:
            bloqueado_hasta = datetime.now() + timedelta(minutes=bloqueo_minutos)
            execute_query(
                "UPDATE usuarios SET intentos_fallo = %s, bloqueado_hasta = %s WHERE id = %s",
                (nuevos_intentos, bloqueado_hasta, user['id']),
                commit=True
            )
            return False, None, f"Demasiados intentos fallidos. Usuario bloqueado por {bloqueo_minutos} minutos"
        else:
            execute_query(
                "UPDATE usuarios SET intentos_fallo = %s WHERE id = %s",
                (nuevos_intentos, user['id']),
                commit=True
            )
            return False, None, "Contraseña incorrecta"

def get_user_permissions(user_id):
    """Obtiene los permisos del usuario"""
    query = """
        SELECT DISTINCT p.nombre_permiso, p.modulo
        FROM usuarios u
        JOIN usuarios_roles ur ON u.id = ur.usuario_id
        JOIN roles_permisos rp ON ur.rol_id = rp.rol_id
        JOIN permisos p ON rp.permiso_id = p.id
        WHERE u.id = %s AND u.activo = true
    """
    return execute_query(query, (user_id,), fetch_all=True) or []

def check_permission(permission_name):
    """Verifica si el usuario actual tiene un permiso específico"""
    if 'user_permissions' not in st.session_state:
        return False
    
    permissions = st.session_state.user_permissions
    return any(p['nombre_permiso'] == permission_name for p in permissions)

def login_form():
    """Muestra el formulario de login"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: white;
    }
    .login-title {
        text-align: center;
        color: #0066cc;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<h1 class="login-title">🏥 Clínica Médica</h1>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align:center">Iniciar Sesión</h3>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario o Email", placeholder="Ingrese su usuario o email")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            submit = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Por favor complete todos los campos")
                else:
                    success, user_data, message = authenticate_user(username, password)
                    
                    if success:
                        # Guardar en sesión
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_data['id']
                        st.session_state.username = user_data['nombre_usuario']
                        st.session_state.user_fullname = user_data['nombre_completo']
                        
                        # Obtener y guardar permisos
                        permissions = get_user_permissions(user_data['id'])
                        st.session_state.user_permissions = permissions
                        
                        # Verificar si requiere cambio de contraseña
                        if user_data['requiere_cambio_contraseña']:
                            st.session_state.require_password_change = True
                            st.rerun()
                        else:
                            st.success(message)
                            st.rerun()
                    else:
                        st.error(message)
        
        st.markdown('</div>', unsafe_allow_html=True)

def logout():
    """Cierra la sesión del usuario"""
    for key in ['authenticated', 'user_id', 'username', 'user_fullname', 'user_permissions']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()