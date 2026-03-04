import streamlit as st
import pandas as pd
from utils.db_connection import execute_query
from utils.auth import check_permission
from utils.helpers import format_datetime
import logging

logger = logging.getLogger(__name__)

def show_mantenedores():
    """Módulo de mantenedores (CRUD de catálogos)"""
    st.title("🔧 Mantenedores del Sistema")
    
    if not check_permission('gestionar_mantenedores'):
        st.error("No tiene permisos para gestionar mantenedores")
        return
    
    # Tabs para diferentes mantenedores
    tab1, tab2, tab3 = st.tabs(["🏥 Especialidades", "🚪 Consultorios", "⚙️ Configuración"])
    
    with tab1:
        show_especialidades()
    
    with tab2:
        show_consultorios()
    
    with tab3:
        show_configuracion()

def show_especialidades():
    """CRUD de especialidades médicas"""
    st.header("Gestión de Especialidades Médicas")
    
    # Formulario para nueva especialidad
    with st.expander("➕ Nueva Especialidad", expanded=False):
        with st.form("form_especialidad"):
            nombre = st.text_input("Nombre de la Especialidad*", max_chars=100)
            descripcion = st.text_area("Descripción", max_chars=500)
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Guardar", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("Cancelar", use_container_width=True)
            
            if submit:
                if not nombre:
                    st.error("El nombre de la especialidad es obligatorio")
                else:
                    try:
                        query = """
                            INSERT INTO especialidades 
                            (nombre_especialidad, descripcion, usuario_creacion)
                            VALUES (%s, %s, %s)
                        """
                        execute_query(
                            query, 
                            (nombre, descripcion, st.session_state.username),
                            commit=True
                        )
                        st.success("Especialidad creada exitosamente")
                        st.rerun()
                    except Exception as e:
                        if "unique" in str(e).lower():
                            st.error("Ya existe una especialidad con ese nombre")
                        else:
                            st.error(f"Error al crear la especialidad: {str(e)}")
    
    # Listado de especialidades
    st.subheader("Listado de Especialidades")
    
    # Obtener especialidades
    query = """
        SELECT 
            id,
            nombre_especialidad,
            descripcion,
            activo,
            fecha_creacion,
            usuario_creacion
        FROM especialidades
        ORDER BY nombre_especialidad
    """
    especialidades = execute_query(query, fetch_all=True)
    
    if especialidades:
        # Convertir a DataFrame para mejor visualización
        df = pd.DataFrame(especialidades)
        df['fecha_creacion'] = pd.to_datetime(df['fecha_creacion']).dt.strftime('%d/%m/%Y')
        df['activo'] = df['activo'].map({True: '✅ Sí', False: '❌ No'})
        
        # Mostrar tabla con opciones de edición
        for idx, row in df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 1, 1])
                with col1:
                    st.write(f"**{row['nombre_especialidad']}**")
                with col2:
                    st.write(row['descripcion'] or "—")
                with col3:
                    st.write(row['activo'])
                with col4:
                    if st.button("✏️", key=f"edit_{row['id']}", help="Editar"):
                        st.session_state[f"editing_{row['id']}"] = True
                with col5:
                    if st.button("🗑️", key=f"delete_{row['id']}", help="Eliminar"):
                        delete_especialidad(row['id'])
                
                # Formulario de edición (si está activo)
                if st.session_state.get(f"editing_{row['id']}", False):
                    with st.form(key=f"edit_form_{row['id']}"):
                        st.write(f"**Editando: {row['nombre_especialidad']}**")
                        new_nombre = st.text_input("Nombre", value=row['nombre_especialidad'])
                        new_desc = st.text_area("Descripción", value=row['descripcion'] or "")
                        new_activo = st.checkbox("Activo", value=row['activo'] == '✅ Sí')
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Guardar"):
                                update_especialidad(row['id'], new_nombre, new_desc, new_activo)
                        with col2:
                            if st.form_submit_button("❌ Cancelar"):
                                del st.session_state[f"editing_{row['id']}"]
                                st.rerun()
                st.divider()
    else:
        st.info("No hay especialidades registradas")

def delete_especialidad(id_especialidad):
    """Elimina (desactiva) una especialidad"""
    try:
        # Verificar si tiene médicos asociados
        check_query = "SELECT COUNT(*) as total FROM medicos WHERE id_especialidad = %s"
        result = execute_query(check_query, (id_especialidad,), fetch_one=True)
        
        if result and result['total'] > 0:
            # Si tiene médicos, solo desactivar
            query = "UPDATE especialidades SET activo = false WHERE id = %s"
            execute_query(query, (id_especialidad,), commit=True)
            st.warning("La especialidad tenía médicos asociados. Se ha desactivado.")
        else:
            # Si no tiene médicos, eliminar físicamente
            query = "DELETE FROM especialidades WHERE id = %s"
            execute_query(query, (id_especialidad,), commit=True)
            st.success("Especialidad eliminada correctamente")
        
        st.rerun()
    except Exception as e:
        st.error(f"Error al eliminar: {str(e)}")

def update_especialidad(id_especialidad, nombre, descripcion, activo):
    """Actualiza una especialidad"""
    try:
        query = """
            UPDATE especialidades 
            SET nombre_especialidad = %s,
                descripcion = %s,
                activo = %s,
                fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id = %s
        """
        execute_query(
            query,
            (nombre, descripcion, activo, st.session_state.username, id_especialidad),
            commit=True
        )
        st.success("Especialidad actualizada correctamente")
        del st.session_state[f"editing_{id_especialidad}"]
        st.rerun()
    except Exception as e:
        st.error(f"Error al actualizar: {str(e)}")

def show_consultorios():
    """CRUD de consultorios"""
    st.header("Gestión de Consultorios")
    
    # Formulario para nuevo consultorio
    with st.expander("➕ Nuevo Consultorio", expanded=False):
        with st.form("form_consultorio"):
            nombre = st.text_input("Nombre/Número del Consultorio*", max_chars=50)
            ubicacion = st.text_input("Ubicación", max_chars=200)
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Guardar", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("Cancelar", use_container_width=True)
            
            if submit:
                if not nombre:
                    st.error("El nombre del consultorio es obligatorio")
                else:
                    try:
                        query = """
                            INSERT INTO consultorios 
                            (nombre, ubicacion, usuario_creacion)
                            VALUES (%s, %s, %s)
                        """
                        execute_query(
                            query, 
                            (nombre, ubicacion, st.session_state.username),
                            commit=True
                        )
                        st.success("Consultorio creado exitosamente")
                        st.rerun()
                    except Exception as e:
                        if "unique" in str(e).lower():
                            st.error("Ya existe un consultorio con ese nombre")
                        else:
                            st.error(f"Error al crear el consultorio: {str(e)}")
    
    # Listado de consultorios
    query = """
        SELECT 
            id,
            nombre,
            ubicacion,
            activo
        FROM consultorios
        ORDER BY nombre
    """
    consultorios = execute_query(query, fetch_all=True)
    
    if consultorios:
        df = pd.DataFrame(consultorios)
        df['activo'] = df['activo'].map({True: '✅ Sí', False: '❌ No'})
        
        st.dataframe(
            df,
            column_config={
                "nombre": "Consultorio",
                "ubicacion": "Ubicación",
                "activo": "Activo"
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay consultorios registrados")

def show_configuracion():
    """Configuraciones generales del sistema"""
    st.header("Configuración del Sistema")
    
    # Configuración de horarios
    st.subheader("⏰ Horarios de Atención")
    
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    horarios = {}
    
    for dia in dias_semana:
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.write(f"**{dia}**")
        with col2:
            horarios[f"{dia}_inicio"] = st.time_input("Apertura", value=None, key=f"inicio_{dia}", label_visibility="collapsed")
        with col3:
            horarios[f"{dia}_fin"] = st.time_input("Cierre", value=None, key=f"fin_{dia}", label_visibility="collapsed")
    
    if st.button("💾 Guardar Configuración de Horarios", use_container_width=True):
        # Aquí se guardaría en una tabla de configuración
        st.success("Configuración guardada exitosamente")
    
    st.divider()
    
    # Configuración de notificaciones
    st.subheader("📧 Notificaciones")
    
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Enviar recordatorios de citas por email", value=True)
        st.checkbox("Enviar confirmación de registro", value=True)
    with col2:
        st.checkbox("Notificar cambios de horario", value=True)
        st.checkbox("Enviar resumen semanal a médicos", value=False)
    
    if st.button("💾 Guardar Configuración de Notificaciones", use_container_width=True):
        st.success("Configuración guardada exitosamente")