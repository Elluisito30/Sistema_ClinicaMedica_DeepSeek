import os
import subprocess
from datetime import datetime
import logging
import pandas as pd
import streamlit as st
from utils.db_connection import execute_query
from utils.auth import check_permission

logger = logging.getLogger(__name__)

def show_backup():
    st.title("💾 Gestión de Backups")
    if not check_permission('gestionar_backups'):
        st.error("No tiene permisos para gestionar backups")
        return
    tab1, tab2 = st.tabs(["🆕 Realizar Backup", "📋 Historial de Backups"])
    with tab1:
        show_realizar_backup()
    with tab2:
        show_historial_backups()

def show_realizar_backup():
    st.header("Realizar Backup de la Base de Datos")
    st.markdown(
        "<div style='background-color: #e8f4fd; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>"
        "<h4 style='margin-top: 0;'>⚠️ Información Importante</h4>"
        "<p>Realizar un backup puede tomar varios minutos dependiendo del tamaño de la base de datos."
        " No cierre la aplicación durante el proceso.</p>"
        "</div>",
        unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)
    with col1:
        tipo_backup = st.radio(
            "Tipo de Backup",
            options=["completo", "incremental"],
            format_func=lambda x: {
                "completo": "💿 Backup Completo (toda la base de datos)",
                "incremental": "📀 Backup Incremental (solo cambios)"
            }[x]
        )
    with col2:
        st.markdown("### 📊 Estadísticas")
        stats = get_database_stats()
        if stats:
            st.metric("Tamaño Base de Datos", stats['tamaño'])
            st.metric("Número de Tablas", stats['tablas'])
            st.metric("Total Registros (estimado)", stats['registros'])
    with st.expander("⚙️ Opciones Avanzadas"):
        col1, col2 = st.columns(2)
        with col1:
            comprimir = st.checkbox("Comprimir backup (formato personalizado)", value=True)
            incluir_blobs = st.checkbox("Incluir datos BLOB", value=True)
        with col2:
            verificar = st.checkbox("Verificar integridad después del backup", value=True)
            notificar = st.checkbox("Notificar por email al finalizar", value=False)
    if st.button("🚀 Iniciar Backup", use_container_width=True, type="primary"):
        with st.spinner("Realizando backup... Esto puede tomar varios minutos."):
            resultado = realizar_backup(tipo_backup, comprimir, incluir_blobs)
            if resultado['exito']:
                st.success("✅ Backup completado exitosamente")
                st.info(f"📁 Archivo: {resultado['archivo']}")
                st.info(f"📊 Tamaño: {resultado['tamaño']}")
                st.balloons()
            else:
                st.error(f"❌ Error al realizar el backup: {resultado['error']}")

def show_historial_backups():
    st.header("Historial de Backups")
    query = """
        SELECT 
            id,
            fecha_inicio,
            fecha_fin,
            tipo,
            estado,
            tamano_mb,
            ruta_archivo,
            usuario_ejecutor,
            observaciones
        FROM registro_backups
        ORDER BY fecha_inicio DESC
        LIMIT 50
    """
    backups = None
    try:
        backups = execute_query(query, fetch_all=True)
    except Exception as e:
        st.info("No hay tabla de historial de backups (registro_backups). Se mostrará vacío.")
        logger.warning(f"Tabla registro_backups no disponible: {e}")
    if backups:
        df = pd.DataFrame(backups)
        if 'fecha_inicio' in df.columns:
            df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.strftime('%d/%m/%Y %H:%M')
        if 'fecha_fin' in df.columns and df['fecha_fin'].notna().any():
            df['fecha_fin'] = pd.to_datetime(df['fecha_fin']).dt.strftime('%d/%m/%Y %H:%M')
        total_backups = len(df)
        exitosos = len(df[df['estado'] == 'exitoso']) if 'estado' in df.columns else 0
        fallidos = len(df[df['estado'] == 'fallido']) if 'estado' in df.columns else 0
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Backups", total_backups)
        with col2:
            st.metric("Exitosos", exitosos)
        with col3:
            st.metric("Fallidos", fallidos)
        with col4:
            tasa_exito = (exitosos / total_backups * 100) if total_backups > 0 else 0
            st.metric("Tasa de Éxito", f"{tasa_exito:.1f}%")
        st.divider()
        st.dataframe(
            df,
            column_config={
                "fecha_inicio": "Inicio",
                "fecha_fin": "Fin",
                "tipo": "Tipo",
                "estado": "Estado",
                "tamano_mb": st.column_config.NumberColumn("Tamaño (MB)", format="%.2f"),
                "ruta_archivo": "Ruta",
                "usuario_ejecutor": "Usuario",
                "observaciones": "Observaciones",
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay registros de backups")

def realizar_backup(tipo_backup="completo", comprimir=True, incluir_blobs=True):
    inicio = datetime.now()
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'db_clinica')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    backup_dir = os.getenv('BACKUP_PATH', './backups')
    pg_dump_path = os.getenv('PG_DUMP_PATH', 'pg_dump')
    try:
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = '.dump' if comprimir else '.sql'
        filename = f"{db_name}_{tipo_backup}_{timestamp}{extension}"
        filepath = os.path.join(backup_dir, filename)
        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password
        cmd = [
            pg_dump_path,
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-d', db_name,
        ]
        if comprimir:
            cmd += ['-Fc']
        else:
            cmd += ['-Fp']
        if not incluir_blobs:
            cmd += ['--exclude-large-objects']
        with open(filepath, 'wb') as out:
            result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, env=env, shell=False)
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            registrar_backup(inicio, None, tipo_backup, 'fallido', 0.0, filepath, error_msg)
            return {'exito': False, 'error': error_msg}
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        fin = datetime.now()
        registrar_backup(inicio, fin, tipo_backup, 'exitoso', size_mb, filepath, None)
        return {'exito': True, 'archivo': filepath, 'tamaño': f"{size_mb:.2f} MB"}
    except FileNotFoundError as e:
        msg = "pg_dump no encontrado. Configure PG_DUMP_PATH en .env"
        registrar_backup(inicio, None, tipo_backup, 'fallido', 0.0, '', msg)
        return {'exito': False, 'error': msg}
    except Exception as e:
        msg = str(e)
        registrar_backup(inicio, None, tipo_backup, 'fallido', 0.0, '', msg)
        return {'exito': False, 'error': msg}

def registrar_backup(inicio, fin, tipo, estado, tamano_mb, ruta, observaciones):
    try:
        execute_query(
            """
            INSERT INTO registro_backups
                (fecha_inicio, fecha_fin, tipo, estado, tamano_mb, ruta_archivo, usuario_ejecutor, observaciones)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                inicio, fin, tipo, estado, tamano_mb, ruta,
                st.session_state.get('username', 'sistema'), observaciones
            ),
            commit=True
        )
    except Exception as e:
        logger.warning(f"No se pudo registrar el backup: {e}")

def get_database_stats():
    try:
        size = execute_query(
            "SELECT pg_size_pretty(pg_database_size(current_database())) AS size",
            fetch_one=True
        )
        tables = execute_query(
            "SELECT COUNT(*) AS count FROM information_schema.tables WHERE table_schema='public'",
            fetch_one=True
        )
        rows = execute_query(
            """
            SELECT COALESCE(SUM(reltuples),0)::bigint AS rows_estimated
            FROM pg_class
            WHERE relkind IN ('r','p')
            """,
            fetch_one=True
        )
        return {
            'tamaño': size['size'] if size else '—',
            'tablas': tables['count'] if tables else 0,
            'registros': int(rows['rows_estimated']) if rows else 0
        }
    except Exception as e:
        logger.warning(f"No se pudieron obtener estadísticas de BD: {e}")
        return None
