import streamlit as st
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la página - DEBE SER LA PRIMERA LLAMADA A STREAMLIT
st.set_page_config(
    page_title="Clínica Médica",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos
from utils.db_connection import test_connection, DatabasePool
from utils.auth import login_form, logout, check_permission
from modules import (
    dashboard,
    mantenedores,
    usuarios,
    procesos,
    reportes,
    backup
)

def main():
    """Función principal de la aplicación"""
    
    # Inicializar sesión
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Verificar autenticación
    if not st.session_state.authenticated:
        # Mostrar formulario de login
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Probar conexión a BD
            if not test_connection():
                st.error("""
                ❌ Error de conexión a la base de datos.
                Por favor, verifique que PostgreSQL esté en ejecución
                y que las credenciales en el archivo .env sean correctas.
                """)
                st.stop()
            
            login_form()
        return
    
    # Usuario autenticado - mostrar aplicación principal
    mostrar_aplicacion()

def mostrar_aplicacion():
    """Muestra la aplicación principal para usuarios autenticados"""
    
    # Barra lateral con menú
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=CLINICA+MEDICA", width=150)
        st.markdown(f"### 👋 Bienvenido, {st.session_state.get('user_fullname', 'Usuario')}")
        st.divider()
        
        # Menú de navegación
        st.markdown("### 📌 Módulos")
        
        # Opciones según permisos
        menu_options = {
            "Dashboard": "📊",
            "Procesos": "📋",
            "Mantenedores": "🔧",
            "Usuarios": "👥",
            "Reportes": "📈",
            "Backup": "💾"
        }
        
        # Verificar permisos para cada módulo
        available_modules = []
        if check_permission('ver_dashboard'):
            available_modules.append("Dashboard")
        if check_permission('ver_citas') or check_permission('crear_citas'):
            available_modules.append("Procesos")
        if check_permission('gestionar_mantenedores'):
            available_modules.append("Mantenedores")
        if check_permission('gestionar_usuarios') or check_permission('gestionar_roles'):
            available_modules.append("Usuarios")
        if check_permission('generar_reportes'):
            available_modules.append("Reportes")
        if check_permission('gestionar_backups'):
            available_modules.append("Backup")
        
        # Selector de módulo
        selected_module = st.radio(
            "Seleccionar Módulo",
            options=available_modules,
            format_func=lambda x: f"{menu_options.get(x, '📁')} {x}",
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Información del sistema
        st.markdown("### ℹ️ Información")
        st.markdown(f"**Usuario:** {st.session_state.get('username', '')}")
        st.markdown(f"**Conexión:** {os.getenv('DB_NAME', 'db_clinica')}")
        
        # Botón de logout
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
    
    # Contenido principal según módulo seleccionado
    st.sidebar.markdown("---")
    
    if selected_module == "Dashboard":
        dashboard.show_dashboard()
    elif selected_module == "Procesos":
        procesos.show_procesos()
    elif selected_module == "Mantenedores":
        mantenedores.show_mantenedores()
    elif selected_module == "Usuarios":
        usuarios.show_usuarios()
    elif selected_module == "Reportes":
        reportes.show_reportes()
    elif selected_module == "Backup":
        backup.show_backup()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
        "© 2024 Clínica Médica<br>Versión 1.0.0"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
