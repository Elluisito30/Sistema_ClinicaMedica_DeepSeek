import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os
from utils.db_connection import execute_query
from utils.auth import check_permission
from utils.helpers import format_currency, format_date
import logging

logger = logging.getLogger(__name__)

def show_reportes():
    """Módulo de reportes y generación de PDF"""
    st.title("📊 Reportes del Sistema")
    
    if not check_permission('generar_reportes'):
        st.error("No tiene permisos para generar reportes")
        return
    
    # Tabs para diferentes tipos de reportes
    tab1, tab2, tab3 = st.tabs([
        "📋 Reportes de Procesos",
        "📈 Reportes de Gestión",
        "📑 Generar PDF"
    ])
    
    with tab1:
        show_reportes_procesos()
    
    with tab2:
        show_reportes_gestion()
    
    with tab3:
        show_generador_pdf()

def show_reportes_procesos():
    """Reportes operativos del sistema"""
    st.header("Reportes de Procesos")
    
    tipo_reporte = st.selectbox(
        "Tipo de Reporte",
        options=[
            "citas_diarias",
            "citas_medico",
            "historial_paciente",
            "facturacion_diaria"
        ],
        format_func=lambda x: {
            "citas_diarias": "📅 Citas por Día",
            "citas_medico": "👨‍⚕️ Citas por Médico",
            "historial_paciente": "📋 Historial de Pacientes",
            "facturacion_diaria": "💰 Facturación Diaria"
        }[x]
    )
    
    # Filtros comunes
    col1, col2 = st.columns(2)
    with col1:
        fecha_desde = st.date_input("Desde", value=datetime.now().date() - timedelta(days=30))
    with col2:
        fecha_hasta = st.date_input("Hasta", value=datetime.now().date())
    
    if st.button("🔍 Generar Reporte", use_container_width=True):
        if tipo_reporte == "citas_diarias":
            generar_reporte_citas_diarias(fecha_desde, fecha_hasta)
        elif tipo_reporte == "citas_medico":
            generar_reporte_citas_medico(fecha_desde, fecha_hasta)
        elif tipo_reporte == "historial_paciente":
            generar_reporte_historial_pacientes(fecha_desde, fecha_hasta)
        elif tipo_reporte == "facturacion_diaria":
            generar_reporte_facturacion_diaria(fecha_desde, fecha_hasta)

def generar_reporte_citas_diarias(desde, hasta):
    """Genera reporte de citas diarias"""
    
    query = """
        SELECT 
            DATE(fecha_hora_cita) as fecha,
            COUNT(*) as total_citas,
            SUM(CASE WHEN estado = 'completada' THEN 1 ELSE 0 END) as completadas,
            SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) as canceladas,
            SUM(CASE WHEN estado = 'programada' THEN 1 ELSE 0 END) as programadas
        FROM citas
        WHERE DATE(fecha_hora_cita) BETWEEN %s AND %s
        GROUP BY DATE(fecha_hora_cita)
        ORDER BY fecha
    """
    
    datos = execute_query(query, (desde, hasta), fetch_all=True)
    
    if datos:
        df = pd.DataFrame(datos)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Citas", df['total_citas'].sum())
        with col2:
            st.metric("Completadas", df['completadas'].sum())
        with col3:
            st.metric("Canceladas", df['canceladas'].sum())
        with col4:
            tasa_exito = (df['completadas'].sum() / df['total_citas'].sum() * 100) if df['total_citas'].sum() > 0 else 0
            st.metric("Tasa de Éxito", f"{tasa_exito:.1f}%")
        
        # Gráfico
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['fecha'],
            y=df['programadas'],
            name='Programadas',
            marker_color='#FFA07A'
        ))
        fig.add_trace(go.Bar(
            x=df['fecha'],
            y=df['completadas'],
            name='Completadas',
            marker_color='#90EE90'
        ))
        fig.add_trace(go.Bar(
            x=df['fecha'],
            y=df['canceladas'],
            name='Canceladas',
            marker_color='#FFB6C1'
        ))
        
        fig.update_layout(
            title="Citas por Día",
            xaxis_title="Fecha",
            yaxis_title="Cantidad",
            barmode='stack',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detalle
        st.subheader("Detalle Diario")
        st.dataframe(
            df,
            column_config={
                "fecha": "Fecha",
                "total_citas": "Total",
                "programadas": "Programadas",
                "completadas": "Completadas",
                "canceladas": "Canceladas"
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay datos para el período seleccionado")

def generar_reporte_citas_medico(desde, hasta):
    """Genera reporte de citas por médico"""
    
    query = """
        SELECT 
            u.nombre_completo as medico,
            e.nombre_especialidad as especialidad,
            COUNT(*) as total_citas,
            COUNT(DISTINCT c.id_paciente) as pacientes_unicos,
            AVG(EXTRACT(EPOCH FROM (h.fecha_atencion - c.fecha_hora_cita))/60)::numeric(10,2) as tiempo_espera_promedio
        FROM citas c
        JOIN medicos m ON c.id_medico = m.id
        JOIN usuarios u ON m.id = u.id
        JOIN especialidades e ON m.id_especialidad = e.id
        LEFT JOIN historial_medico h ON c.id = h.id_cita
        WHERE DATE(c.fecha_hora_cita) BETWEEN %s AND %s
        AND c.estado = 'completada'
        GROUP BY u.nombre_completo, e.nombre_especialidad
        ORDER BY total_citas DESC
    """
    
    datos = execute_query(query, (desde, hasta), fetch_all=True)
    
    if datos:
        df = pd.DataFrame(datos)
        
        # Gráfico de barras
        fig = px.bar(
            df,
            x='medico',
            y='total_citas',
            color='especialidad',
            title="Citas por Médico",
            labels={'total_citas': 'Total Citas', 'medico': 'Médico'}
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detalle
        st.subheader("Detalle por Médico")
        st.dataframe(
            df,
            column_config={
                "medico": "Médico",
                "especialidad": "Especialidad",
                "total_citas": "Total Citas",
                "pacientes_unicos": "Pacientes Únicos",
                "tiempo_espera_promedio": st.column_config.NumberColumn(
                    "Tiempo Espera Prom.",
                    format="%.0f min"
                )
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay datos para el período seleccionado")

def generar_reporte_historial_pacientes(desde, hasta):
    """Genera reporte de historial de pacientes atendidos"""
    
    query = """
        SELECT 
            u.nombre_completo as paciente,
            COUNT(DISTINCT h.id) as total_atenciones,
            COUNT(DISTINCT m.id_especialidad) as especialidades_atendidas,
            MIN(h.fecha_atencion) as primera_atencion,
            MAX(h.fecha_atencion) as ultima_atencion,
            STRING_AGG(DISTINCT e.nombre_especialidad, ', ') as especialidades
        FROM historial_medico h
        JOIN pacientes p ON h.id_paciente = p.id
        JOIN usuarios u ON p.id = u.id
        JOIN medicos m ON h.id_medico = m.id
        JOIN especialidades e ON m.id_especialidad = e.id
        WHERE DATE(h.fecha_atencion) BETWEEN %s AND %s
        GROUP BY u.nombre_completo
        ORDER BY total_atenciones DESC
        LIMIT 20
    """
    
    datos = execute_query(query, (desde, hasta), fetch_all=True)
    
    if datos:
        df = pd.DataFrame(datos)
        
        # Top pacientes
        st.subheader("Top 20 Pacientes por Atenciones")
        st.dataframe(
            df,
            column_config={
                "paciente": "Paciente",
                "total_atenciones": "Atenciones",
                "especialidades_atendidas": "Especialidades",
                "primera_atencion": "Primera Atención",
                "ultima_atencion": "Última Atención",
                "especialidades": "Especialidades Atendidas"
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay datos para el período seleccionado")

def generar_reporte_facturacion_diaria(desde, hasta):
    """Genera reporte de facturación diaria"""
    
    query = """
        SELECT 
            DATE(fecha_emision) as fecha,
            COUNT(*) as facturas_emitidas,
            SUM(CASE WHEN estado_pago = 'pagado' THEN monto_total ELSE 0 END) as ingresos,
            SUM(CASE WHEN estado_pago = 'pendiente' THEN monto_total ELSE 0 END) as pendiente,
            AVG(monto_total) as ticket_promedio
        FROM facturas
        WHERE DATE(fecha_emision) BETWEEN %s AND %s
        GROUP BY DATE(fecha_emision)
        ORDER BY fecha
    """
    
    datos = execute_query(query, (desde, hasta), fetch_all=True)
    
    if datos:
        df = pd.DataFrame(datos)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Facturas Emitidas", df['facturas_emitidas'].sum())
        with col2:
            st.metric("Ingresos", format_currency(df['ingresos'].sum()))
        with col3:
            st.metric("Pendiente", format_currency(df['pendiente'].sum()))
        with col4:
            st.metric("Ticket Promedio", format_currency(df['ticket_promedio'].mean()))
        
        # Gráfico de línea
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['fecha'],
            y=df['ingresos'],
            mode='lines+markers',
            name='Ingresos',
            line=dict(color='green', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df['fecha'],
            y=df['pendiente'],
            mode='lines+markers',
            name='Pendiente',
            line=dict(color='orange', width=2)
        ))
        
        fig.update_layout(
            title="Evolución de Facturación",
            xaxis_title="Fecha",
            yaxis_title="Monto ($)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detalle
        st.dataframe(
            df,
            column_config={
                "fecha": "Fecha",
                "facturas_emitidas": "Facturas",
                "ingresos": st.column_config.NumberColumn("Ingresos", format="$%.2f"),
                "pendiente": st.column_config.NumberColumn("Pendiente", format="$%.2f"),
                "ticket_promedio": st.column_config.NumberColumn("Ticket Prom.", format="$%.2f")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay datos para el período seleccionado")

def show_reportes_gestion():
    """Reportes de gestión y análisis"""
    st.header("Reportes de Gestión")
    
    tipo_reporte = st.selectbox(
        "Tipo de Reporte de Gestión",
        options=[
            "productividad_medica",
            "satisfaccion_pacientes",
            "analisis_financiero",
            "ocupacion_recursos"
        ],
        format_func=lambda x: {
            "productividad_medica": "📊 Productividad Médica",
            "satisfaccion_pacientes": "⭐ Satisfacción de Pacientes",
            "analisis_financiero": "💰 Análisis Financiero",
            "ocupacion_recursos": "🏥 Ocupación de Recursos"
        }[x]
    )
    
    # Selector de período
    periodo = st.selectbox(
        "Período",
        options=["mensual", "trimestral", "semestral", "anual"],
        format_func=lambda x: {
            "mensual": "Mensual",
            "trimestral": "Trimestral",
            "semestral": "Semestral",
            "anual": "Anual"
        }[x]
    )
    
    if st.button("📊 Generar Análisis", use_container_width=True):
        if tipo_reporte == "productividad_medica":
            generar_reporte_productividad(periodo)
        elif tipo_reporte == "satisfaccion_pacientes":
            generar_reporte_satisfaccion(periodo)
        elif tipo_reporte == "analisis_financiero":
            generar_reporte_financiero(periodo)
        elif tipo_reporte == "ocupacion_recursos":
            generar_reporte_ocupacion(periodo)

def generar_reporte_productividad(periodo):
    """Genera reporte de productividad médica"""
    
    # Determinar agrupación según período
    group_by = {
        "mensual": "DATE_TRUNC('month', fecha_hora_cita)",
        "trimestral": "DATE_TRUNC('quarter', fecha_hora_cita)",
        "semestral": "CONCAT(EXTRACT(YEAR FROM fecha_hora_cita), '-S', CEIL(EXTRACT(MONTH FROM fecha_hora_cita)/6))",
        "anual": "EXTRACT(YEAR FROM fecha_hora_cita)"
    }[periodo]
    
    query = f"""
        SELECT 
            {group_by} as periodo,
            u.nombre_completo as medico,
            e.nombre_especialidad as especialidad,
            COUNT(*) as citas_atendidas,
            COUNT(DISTINCT c.id_paciente) as pacientes_unicos
        FROM citas c
        JOIN medicos m ON c.id_medico = m.id
        JOIN usuarios u ON m.id = u.id
        JOIN especialidades e ON m.id_especialidad = e.id
        WHERE c.estado = 'completada'
        GROUP BY periodo, u.nombre_completo, e.nombre_especialidad
        ORDER BY periodo DESC, citas_atendidas DESC
    """
    
    datos = execute_query(query, fetch_all=True)
    
    if datos:
        df = pd.DataFrame(datos)
        
        # Gráfico comparativo
        fig = px.bar(
            df,
            x='medico',
            y='citas_atendidas',
            color='especialidad',
            facet_row='periodo',
            title="Productividad por Médico y Período"
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla resumen
        st.subheader("Resumen de Productividad")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos suficientes para generar el reporte")

def generar_reporte_satisfaccion(periodo):
    """Genera reporte de satisfacción de pacientes"""
    st.info("Módulo de satisfacción en desarrollo")
    # Aquí irían consultas de encuestas de satisfacción

def generar_reporte_financiero(periodo):
    """Genera análisis financiero"""
    
    query = """
        SELECT 
            EXTRACT(YEAR FROM fecha_emision) as año,
            EXTRACT(MONTH FROM fecha_emision) as mes,
            COUNT(*) as facturas_emitidas,
            SUM(CASE WHEN estado_pago = 'pagado' THEN monto_total ELSE 0 END) as ingresos,
            SUM(CASE WHEN estado_pago = 'pendiente' THEN monto_total ELSE 0 END) as cuentas_cobrar,
            AVG(monto_total) as ticket_promedio
        FROM facturas
        WHERE fecha_emision >= CURRENT_DATE - INTERVAL '1 year'
        GROUP BY año, mes
        ORDER BY año DESC, mes DESC
    """
    
    datos = execute_query(query, fetch_all=True)
    
    if datos:
        df = pd.DataFrame(datos)
        df['periodo'] = df['año'].astype(int).astype(str) + '-' + df['mes'].astype(int).astype(str).str.zfill(2)
        
        # Gráfico de ingresos por mes
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['periodo'],
            y=df['ingresos'],
            name='Ingresos',
            marker_color='green'
        ))
        fig.add_trace(go.Scatter(
            x=df['periodo'],
            y=df['cuentas_cobrar'],
            name='Cuentas por Cobrar',
            mode='lines+markers',
            line=dict(color='orange', width=2)
        ))
        
        fig.update_layout(
            title="Evolución Financiera - Últimos 12 Meses",
            xaxis_title="Período",
            yaxis_title="Monto ($)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Ingresos Año", format_currency(df['ingresos'].sum()))
        with col2:
            st.metric("Cuentas por Cobrar", format_currency(df['cuentas_cobrar'].sum()))
        with col3:
            st.metric("Ticket Promedio", format_currency(df['ticket_promedio'].mean()))
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos financieros disponibles")

def generar_reporte_ocupacion(periodo):
    """Genera reporte de ocupación de recursos"""
    
    query = """
        SELECT 
            cons.nombre as consultorio,
            COUNT(*) as citas_realizadas,
            COUNT(DISTINCT DATE(c.fecha_hora_cita)) as dias_ocupado,
            COUNT(DISTINCT m.id) as medicos_diferentes
        FROM citas c
        JOIN consultorios cons ON c.id_consultorio = cons.id
        JOIN medicos m ON c.id_medico = m.id
        WHERE c.estado = 'completada'
        AND c.fecha_hora_cita >= CURRENT_DATE - INTERVAL '3 months'
        GROUP BY cons.nombre
        ORDER BY citas_realizadas DESC
    """
    
    datos = execute_query(query, fetch_all=True)
    
    if datos:
        df = pd.DataFrame(datos)
        
        # Calcular tasa de ocupación
        dias_totales = 90  # 3 meses
        df['tasa_ocupacion'] = (df['dias_ocupado'] / dias_totales * 100).round(1)
        
        # Gráfico
        fig = px.bar(
            df,
            x='consultorio',
            y='tasa_ocupacion',
            title="Tasa de Ocupación por Consultorio (Últimos 3 meses)",
            labels={'tasa_ocupacion': 'Tasa de Ocupación (%)'},
            color='tasa_ocupacion',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos de ocupación disponibles")

def show_generador_pdf():
    """Generador de reportes PDF"""
    st.header("Generar Reporte PDF")
    
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='margin-top: 0;'>📄 Generación de Reportes en PDF</h4>
        <p>Seleccione el tipo de reporte y el período para generar un documento PDF profesional con gráficos y tablas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_reporte_pdf = st.selectbox(
            "Tipo de Reporte PDF",
            options=[
                "reporte_citas",
                "reporte_facturacion",
                "reporte_productividad",
                "reporte_completo"
            ],
            format_func=lambda x: {
                "reporte_citas": "📅 Reporte de Citas",
                "reporte_facturacion": "💰 Reporte de Facturación",
                "reporte_productividad": "📊 Reporte de Productividad",
                "reporte_completo": "📋 Reporte Ejecutivo Completo"
            }[x]
        )
    
    with col2:
        periodo_pdf = st.selectbox(
            "Período",
            options=["semana", "mes", "trimestre", "año"],
            format_func=lambda x: {
                "semana": "Última Semana",
                "mes": "Último Mes",
                "trimestre": "Último Trimestre",
                "año": "Último Año"
            }[x]
        )
    
    if st.button("📥 Generar y Descargar PDF", use_container_width=True):
        with st.spinner("Generando reporte PDF..."):
            pdf_file = generar_pdf(tipo_reporte_pdf, periodo_pdf)
            
            if pdf_file:
                with open(pdf_file, "rb") as f:
                    pdf_data = f.read()
                
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_data,
                    file_name=f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Limpiar archivo temporal
                os.unlink(pdf_file)

def generar_pdf(tipo_reporte, periodo):
    """Genera un reporte en PDF"""
    
    # Determinar rango de fechas
    fecha_fin = datetime.now()
    if periodo == "semana":
        fecha_inicio = fecha_fin - timedelta(days=7)
    elif periodo == "mes":
        fecha_inicio = fecha_fin - timedelta(days=30)
    elif periodo == "trimestre":
        fecha_inicio = fecha_fin - timedelta(days=90)
    else:  # año
        fecha_inicio = fecha_fin - timedelta(days=365)
    
    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Clínica Médica - Reporte de Gestión', 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Período: {fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}', 0, 1, 'C')
    pdf.cell(0, 10, f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
    pdf.line(10, 40, 200, 40)
    pdf.ln(10)
    
    # Contenido según tipo
    if tipo_reporte in ["reporte_citas", "reporte_completo"]:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Resumen de Citas', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        query_citas = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado = 'completada' THEN 1 ELSE 0 END) as completadas,
                SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) as canceladas,
                SUM(CASE WHEN estado = 'programada' THEN 1 ELSE 0 END) as programadas
            FROM citas
            WHERE fecha_hora_cita BETWEEN %s AND %s
        """
        resumen = execute_query(query_citas, (fecha_inicio, fecha_fin), fetch_one=True)
        
        if resumen:
            pdf.cell(0, 8, f'Total Citas: {resumen["total"]}', 0, 1)
            pdf.cell(0, 8, f'Completadas: {resumen["completadas"]}', 0, 1)
            pdf.cell(0, 8, f'Canceladas: {resumen["canceladas"]}', 0, 1)
            pdf.cell(0, 8, f'Programadas: {resumen["programadas"]}', 0, 1)
        pdf.ln(5)
    
    if tipo_reporte in ["reporte_facturacion", "reporte_completo"]:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Resumen Financiero', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        query_finanzas = """
            SELECT 
                COALESCE(SUM(CASE WHEN estado_pago = 'pagado' THEN monto_total ELSE 0 END), 0) as ingresos,
                COALESCE(SUM(CASE WHEN estado_pago = 'pendiente' THEN monto_total ELSE 0 END), 0) as pendiente,
                COUNT(*) as facturas
            FROM facturas
            WHERE fecha_emision BETWEEN %s AND %s
        """
        finanzas = execute_query(query_finanzas, (fecha_inicio, fecha_fin), fetch_one=True)
        
        if finanzas:
            pdf.cell(0, 8, f'Ingresos: ${finanzas["ingresos"]:,.2f}', 0, 1)
            pdf.cell(0, 8, f'Pendiente: ${finanzas["pendiente"]:,.2f}', 0, 1)
            pdf.cell(0, 8, f'Facturas Emitidas: {finanzas["facturas"]}', 0, 1)
        pdf.ln(5)
    
    if tipo_reporte in ["reporte_productividad", "reporte_completo"]:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Top 5 Médicos por Atenciones', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        query_medicos = """
            SELECT 
                u.nombre_completo,
                COUNT(*) as atenciones
            FROM citas c
            JOIN medicos m ON c.id_medico = m.id
            JOIN usuarios u ON m.id = u.id
            WHERE c.estado = 'completada'
            AND c.fecha_hora_cita BETWEEN %s AND %s
            GROUP BY u.nombre_completo
            ORDER BY atenciones DESC
            LIMIT 5
        """
        medicos = execute_query(query_medicos, (fecha_inicio, fecha_fin), fetch_all=True)
        
        if medicos:
            for i, medico in enumerate(medicos, 1):
                pdf.cell(0, 8, f'{i}. {medico["nombre_completo"]}: {medico["atenciones"]} atenciones', 0, 1)
    
    # Guardar PDF temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name
    
    return None