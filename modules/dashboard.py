import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.db_connection import execute_query
from utils.helpers import (
    create_bar_chart, create_line_chart, create_pie_chart,
    format_currency, display_metric_card, get_date_range
)
from utils.auth import check_permission
import logging

logger = logging.getLogger(__name__)

def show_dashboard():
    """Muestra el dashboard principal con KPIs y gráficos"""
    st.title("📊 Dashboard Ejecutivo")
    
    # Verificar permiso
    if not check_permission('ver_dashboard'):
        st.error("No tiene permisos para ver el dashboard")
        return
    
    # Selector de período
    col1, col2 = st.columns([3, 1])
    with col2:
        period = st.selectbox(
            "Período",
            options=["today", "week", "month", "year"],
            format_func=lambda x: {
                "today": "Hoy",
                "week": "Esta Semana",
                "month": "Este Mes",
                "year": "Este Año"
            }[x]
        )
    
    # Obtener fechas del período
    start_date, end_date = get_date_range(period)
    
    # Métricas principales en fila
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Citas hoy
        citas_hoy = get_citas_count(datetime.now().date())
        display_metric_card(
            "Citas Hoy",
            citas_hoy,
            help_text="Citas programadas para hoy"
        )
    
    with col2:
        # Pacientes nuevos en el período
        pacientes_nuevos = get_pacientes_nuevos(start_date, end_date)
        display_metric_card(
            "Pacientes Nuevos",
            pacientes_nuevos,
            help_text=f"Desde {start_date.strftime('%d/%m')}"
        )
    
    with col3:
        # Ingresos del período
        ingresos = get_ingresos_periodo(start_date, end_date)
        display_metric_card(
            "Ingresos",
            format_currency(ingresos),
            help_text=f"Total facturado en el período"
        )
    
    with col4:
        # Ocupación de consultorios
        ocupacion = get_ocupacion_consultorios()
        display_metric_card(
            "Ocupación",
            f"{ocupacion}%",
            help_text="Promedio de ocupación hoy"
        )
    
    st.divider()
    
    # Gráficos en dos columnas
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico: Citas por especialidad
        st.subheader("📊 Citas por Especialidad")
        citas_especialidad = get_citas_por_especialidad(start_date, end_date)
        if not citas_especialidad.empty:
            fig = create_bar_chart(
                citas_especialidad,
                x='especialidad',
                y='total',
                title="Distribución de Citas por Especialidad",
                color='especialidad'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para el período seleccionado")
    
    with col2:
        # Gráfico: Evolución diaria de pacientes
        st.subheader("📈 Evolución de Atenciones")
        evolucion = get_evolucion_atenciones(start_date, end_date)
        if not evolucion.empty:
            fig = create_line_chart(
                evolucion,
                x='fecha',
                y='total',
                title="Pacientes Atendidos por Día"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para el período seleccionado")
    
    # Segunda fila de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico: Distribución por edad/género
        st.subheader("👥 Distribución Demográfica")
        demografia = get_distribucion_demografica()
        if not demografia.empty:
            fig = create_pie_chart(
                demografia,
                values='cantidad',
                names='rango_edad',
                title="Pacientes por Rango de Edad"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos demográficos disponibles")
    
    with col2:
        # Top médicos por atención
        st.subheader("👨‍⚕️ Top Médicos")
        top_medicos = get_top_medicos(start_date, end_date)
        if not top_medicos.empty:
            st.dataframe(
                top_medicos,
                column_config={
                    "medico": "Médico",
                    "atenciones": "Atenciones",
                    "especialidad": "Especialidad"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay datos de médicos para el período")
    
    # Alertas y notificaciones
    st.divider()
    st.subheader("🔔 Alertas del Sistema")
    
    alertas = get_alertas_sistema()
    if alertas:
        for alerta in alertas:
            if alerta['tipo'] == 'warning':
                st.warning(alerta['mensaje'])
            elif alerta['tipo'] == 'error':
                st.error(alerta['mensaje'])
            else:
                st.info(alerta['mensaje'])
    else:
        st.success("✅ Todo en orden. No hay alertas activas")

# Funciones de consulta para el dashboard
def get_citas_count(fecha):
    """Obtiene el número de citas para una fecha específica"""
    query = """
        SELECT COUNT(*) as total
        FROM citas
        WHERE DATE(fecha_hora_cita) = %s
    """
    result = execute_query(query, (fecha,), fetch_one=True)
    return result['total'] if result else 0

def get_pacientes_nuevos(start_date, end_date):
    """Obtiene pacientes nuevos en el período"""
    query = """
        SELECT COUNT(*) as total
        FROM usuarios u
        JOIN pacientes p ON u.id = p.id
        WHERE DATE(u.fecha_creacion) BETWEEN %s AND %s
    """
    result = execute_query(query, (start_date, end_date), fetch_one=True)
    return result['total'] if result else 0

def get_ingresos_periodo(start_date, end_date):
    """Obtiene total de ingresos en el período"""
    query = """
        SELECT COALESCE(SUM(monto_total), 0) as total
        FROM facturas
        WHERE DATE(fecha_emision) BETWEEN %s AND %s
        AND estado_pago = 'pagado'
    """
    result = execute_query(query, (start_date, end_date), fetch_one=True)
    return float(result['total']) if result else 0.0

def get_ocupacion_consultorios():
    """Calcula el porcentaje de ocupación de consultorios para hoy"""
    query = """
        WITH horarios_totales AS (
            SELECT COUNT(DISTINCT id) as total_consultorios
            FROM consultorios
            WHERE activo = true
        ),
        citas_hoy AS (
            SELECT COUNT(DISTINCT id_consultorio) as consultorios_ocupados
            FROM citas
            WHERE DATE(fecha_hora_cita) = CURRENT_DATE
            AND estado NOT IN ('cancelada')
        )
        SELECT 
            CASE 
                WHEN ht.total_consultorios > 0 
                THEN (co.consultorios_ocupados * 100.0 / ht.total_consultorios)
                ELSE 0 
            END as porcentaje
        FROM horarios_totales ht, citas_hoy co
    """
    result = execute_query(query, fetch_one=True)
    return round(float(result['porcentaje'])) if result else 0

def get_citas_por_especialidad(start_date, end_date):
    """Obtiene distribución de citas por especialidad"""
    query = """
        SELECT 
            e.nombre_especialidad as especialidad,
            COUNT(*) as total
        FROM citas c
        JOIN medicos m ON c.id_medico = m.id
        JOIN especialidades e ON m.id_especialidad = e.id
        WHERE DATE(c.fecha_hora_cita) BETWEEN %s AND %s
        GROUP BY e.nombre_especialidad
        ORDER BY total DESC
    """
    result = execute_query(query, (start_date, end_date), fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def get_evolucion_atenciones(start_date, end_date):
    """Obtiene evolución diaria de atenciones"""
    query = """
        SELECT 
            DATE(fecha_hora_cita) as fecha,
            COUNT(*) as total
        FROM citas
        WHERE DATE(fecha_hora_cita) BETWEEN %s AND %s
        AND estado = 'completada'
        GROUP BY DATE(fecha_hora_cita)
        ORDER BY fecha
    """
    result = execute_query(query, (start_date, end_date), fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def get_distribucion_demografica():
    """Obtiene distribución de pacientes por rango de edad"""
    query = """
        SELECT 
            CASE 
                WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) < 18 THEN '0-17'
                WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 18 AND 30 THEN '18-30'
                WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 31 AND 50 THEN '31-50'
                WHEN EXTRACT(YEAR FROM AGE(fecha_nacimiento)) BETWEEN 51 AND 65 THEN '51-65'
                ELSE '65+'
            END as rango_edad,
            COUNT(*) as cantidad
        FROM pacientes
        GROUP BY rango_edad
        ORDER BY rango_edad
    """
    result = execute_query(query, fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def get_top_medicos(start_date, end_date):
    """Obtiene top médicos por atenciones"""
    query = """
        SELECT 
            u.nombre_completo as medico,
            e.nombre_especialidad as especialidad,
            COUNT(*) as atenciones
        FROM citas c
        JOIN medicos m ON c.id_medico = m.id
        JOIN usuarios u ON m.id = u.id
        JOIN especialidades e ON m.id_especialidad = e.id
        WHERE DATE(c.fecha_hora_cita) BETWEEN %s AND %s
        AND c.estado = 'completada'
        GROUP BY u.nombre_completo, e.nombre_especialidad
        ORDER BY atenciones DESC
        LIMIT 5
    """
    result = execute_query(query, (start_date, end_date), fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def get_alertas_sistema():
    """Obtiene alertas del sistema"""
    alertas = []
    
    # Alertas de stock de citas disponibles
    query_citas_disponibles = """
        SELECT COUNT(*) as citas_programadas
        FROM citas
        WHERE DATE(fecha_hora_cita) = CURRENT_DATE
        AND estado = 'programada'
    """
    result = execute_query(query_citas_disponibles, fetch_one=True)
    if result and result['citas_programadas'] > 50:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f"Alta demanda: {result['citas_programadas']} citas programadas para hoy"
        })
    
    # Alertas de facturas pendientes
    query_facturas_pendientes = """
        SELECT COUNT(*) as pendientes
        FROM facturas
        WHERE estado_pago = 'pendiente'
        AND fecha_emision < CURRENT_DATE - INTERVAL '7 days'
    """
    result = execute_query(query_facturas_pendientes, fetch_one=True)
    if result and result['pendientes'] > 0:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f"{result['pendientes']} facturas tienen más de 7 días sin pagar"
        })
    
    # Alertas de médicos sin disponibilidad
    query_medicos_sin_disponibilidad = """
        SELECT COUNT(*) as sin_disponibilidad
        FROM medicos m
        JOIN usuarios u ON m.id = u.id
        WHERE u.activo = true
        AND NOT EXISTS (
            SELECT 1 FROM citas c
            WHERE c.id_medico = m.id
            AND DATE(c.fecha_hora_cita) = CURRENT_DATE
        )
    """
    result = execute_query(query_medicos_sin_disponibilidad, fetch_one=True)
    if result and result['sin_disponibilidad'] > 3:
        alertas.append({
            'tipo': 'info',
            'mensaje': f"{result['sin_disponibilidad']} médicos sin citas agendadas para hoy"
        })
    
    return alertas