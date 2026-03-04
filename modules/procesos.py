import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from utils.db_connection import execute_query
from utils.auth import check_permission
from utils.helpers import format_datetime, format_date, parse_json_field
import logging

logger = logging.getLogger(__name__)

def show_procesos():
    """Módulo de procesos clínicos"""
    st.title("📋 Procesos Clínicos")
    
    # Tabs para diferentes procesos
    tab1, tab2, tab3 = st.tabs(["📅 Citas Médicas", "📝 Historial Médico", "💰 Facturación"])
    
    with tab1:
        show_gestion_citas()
    
    with tab2:
        show_historial_medico()
    
    with tab3:
        show_facturacion()

def show_gestion_citas():
    """Gestión de citas médicas"""
    st.header("Agendamiento de Citas")
    
    # Verificar permisos
    if not check_permission('ver_citas'):
        st.error("No tiene permisos para ver citas")
        return
    
    # Selector de vista
    vista = st.radio(
        "Vista",
        options=["agendar", "listado", "calendario"],
        format_func=lambda x: {
            "agendar": "➕ Agendar Nueva Cita",
            "listado": "📋 Listado de Citas",
            "calendario": "📅 Vista Calendario"
        }[x],
        horizontal=True
    )
    
    if vista == "agendar":
        form_agendar_cita()
    elif vista == "listado":
        listado_citas()
    else:
        vista_calendario()

def form_agendar_cita():
    """Formulario para agendar nueva cita"""
    st.subheader("Agendar Nueva Cita")
    
    with st.form("form_cita"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Buscar paciente
            pacientes = get_pacientes_activos()
            if pacientes.empty:
                st.warning("No hay pacientes registrados")
                paciente_id = None
            else:
                paciente_id = st.selectbox(
                    "Paciente*",
                    options=pacientes['id'].tolist(),
                    format_func=lambda x: pacientes[pacientes['id'] == x]['nombre'].iloc[0]
                )
        
        with col2:
            # Seleccionar especialidad primero
            especialidades = get_especialidades_activas()
            if especialidades.empty:
                st.warning("No hay especialidades registradas")
                especialidad_id = None
            else:
                especialidad_id = st.selectbox(
                    "Especialidad*",
                    options=especialidades['id'].tolist(),
                    format_func=lambda x: especialidades[especialidades['id'] == x]['nombre'].iloc[0]
                )
        
        # Médicos según especialidad
        if especialidad_id:
            medicos = get_medicos_por_especialidad(especialidad_id)
            if medicos.empty:
                st.warning("No hay médicos disponibles para esta especialidad")
                medico_id = None
            else:
                medico_id = st.selectbox(
                    "Médico*",
                    options=medicos['id'].tolist(),
                    format_func=lambda x: medicos[medicos['id'] == x]['nombre'].iloc[0]
                )
        else:
            medico_id = None
        
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha_cita = st.date_input(
                "Fecha de la Cita*",
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=1)
            )
        with col2:
            hora_cita = st.time_input(
                "Hora de la Cita*",
                value=time(9, 0)  # 9:00 AM por defecto
            )
        with col3:
            consultorios = get_consultorios_activos()
            if not consultorios.empty:
                consultorio_id = st.selectbox(
                    "Consultorio",
                    options=consultorios['id'].tolist(),
                    format_func=lambda x: consultorios[consultorios['id'] == x]['nombre'].iloc[0]
                )
            else:
                consultorio_id = None
        
        motivo = st.text_area("Motivo de la Consulta", max_chars=500)
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Agendar Cita", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Limpiar", use_container_width=True)
        
        if submit:
            if not all([paciente_id, medico_id, fecha_cita, hora_cita]):
                st.error("Todos los campos marcados con * son obligatorios")
            else:
                agendar_cita(paciente_id, medico_id, consultorio_id, fecha_cita, hora_cita, motivo)

def agendar_cita(paciente_id, medico_id, consultorio_id, fecha, hora, motivo):
    """Agenda una nueva cita médica"""
    try:
        # Combinar fecha y hora
        fecha_hora = datetime.combine(fecha, hora)
        
        # Verificar disponibilidad
        if not verificar_disponibilidad(medico_id, fecha_hora):
            st.error("El médico no está disponible en ese horario")
            return
        
        query = """
            INSERT INTO citas 
            (id_paciente, id_medico, id_consultorio, fecha_hora_cita, motivo_consulta, 
             estado, usuario_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        execute_query(
            query,
            (paciente_id, medico_id, consultorio_id, fecha_hora, motivo,
             'programada', st.session_state.username),
            commit=True
        )
        
        st.success("Cita agendada exitosamente")
        st.balloons()
        
    except Exception as e:
        if "unique" in str(e).lower():
            st.error("El médico ya tiene una cita agendada en ese horario")
        else:
            st.error(f"Error al agendar la cita: {str(e)}")

def verificar_disponibilidad(medico_id, fecha_hora):
    """Verifica si un médico está disponible en una fecha y hora específica"""
    # Verificar si ya tiene cita
    query = """
        SELECT COUNT(*) as total
        FROM citas
        WHERE id_medico = %s
        AND fecha_hora_cita = %s
        AND estado NOT IN ('cancelada')
    """
    result = execute_query(query, (medico_id, fecha_hora), fetch_one=True)
    
    if result and result['total'] > 0:
        return False
    
    # Verificar horario de atención del médico
    query_horario = """
        SELECT horario_atencion
        FROM medicos
        WHERE id = %s
    """
    horario = execute_query(query_horario, (medico_id,), fetch_one=True)
    
    if horario and horario['horario_atencion']:
        # Aquí se implementaría la lógica de validación de horario
        # Por ahora, asumimos que está disponible
        pass
    
    return True

def listado_citas():
    """Muestra listado de citas con filtros"""
    st.subheader("Listado de Citas")
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fecha_desde = st.date_input(
            "Desde",
            value=datetime.now().date(),
            key="filtro_desde"
        )
    with col2:
        fecha_hasta = st.date_input(
            "Hasta",
            value=datetime.now().date() + timedelta(days=7),
            key="filtro_hasta"
        )
    with col3:
        estado = st.selectbox(
            "Estado",
            options=["todas", "programada", "confirmada", "en_consulta", "completada", "cancelada"]
        )
    with col4:
        medico = st.selectbox(
            "Médico",
            options=["todos"] + [m['nombre'] for m in get_medicos_lista()]
        )
    
    # Obtener citas
    citas = get_citas_con_filtros(fecha_desde, fecha_hasta, estado, medico)
    
    if citas:
        for cita in citas:
            with st.container():
                # Determinar color según estado
                estado_colors = {
                    'programada': '🔵',
                    'confirmada': '🟢',
                    'en_consulta': '🟡',
                    'completada': '✅',
                    'cancelada': '❌'
                }
                
                col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 2, 2, 1.5, 1.5, 1])
                
                with col1:
                    st.write(f"**{format_datetime(cita['fecha_hora_cita'])}**")
                with col2:
                    st.write(cita['paciente'])
                with col3:
                    st.write(cita['medico'])
                with col4:
                    st.write(cita['especialidad'])
                with col5:
                    st.write(f"{estado_colors.get(cita['estado'], '⚪')} {cita['estado'].title()}")
                with col6:
                    if cita['estado'] == 'programada' and check_permission('editar_citas'):
                        if st.button("✅ Confirmar", key=f"conf_{cita['id']}"):
                            actualizar_estado_cita(cita['id'], 'confirmada')
                with col7:
                    if cita['estado'] in ['programada', 'confirmada'] and check_permission('editar_citas'):
                        if st.button("❌ Cancelar", key=f"cancel_{cita['id']}"):
                            actualizar_estado_cita(cita['id'], 'cancelada')
                
                # Botón para iniciar consulta
                if cita['estado'] == 'confirmada' and check_permission('atender_citas'):
                    col1, col2, col3 = st.columns([1, 1, 8])
                    with col1:
                        if st.button("▶️ Iniciar Consulta", key=f"start_{cita['id']}"):
                            actualizar_estado_cita(cita['id'], 'en_consulta')
                            st.session_state['cita_activa'] = cita['id']
                            st.rerun()
                
                st.divider()
    else:
        st.info("No se encontraron citas con los filtros seleccionados")

def vista_calendario():
    """Vista de calendario de citas"""
    st.subheader("Calendario de Citas")
    
    # Selector de fecha
    fecha = st.date_input(
        "Seleccionar Fecha",
        value=datetime.now().date()
    )
    
    # Obtener citas del día
    query = """
        SELECT 
            c.fecha_hora_cita,
            u.nombre_completo as paciente,
            m_nombre.nombre_completo as medico,
            e.nombre_especialidad as especialidad,
            cons.nombre as consultorio,
            c.estado
        FROM citas c
        JOIN pacientes p ON c.id_paciente = p.id
        JOIN usuarios u ON p.id = u.id
        JOIN medicos m ON c.id_medico = m.id
        JOIN usuarios m_nombre ON m.id = m_nombre.id
        JOIN especialidades e ON m.id_especialidad = e.id
        LEFT JOIN consultorios cons ON c.id_consultorio = cons.id
        WHERE DATE(c.fecha_hora_cita) = %s
        ORDER BY c.fecha_hora_cita
    """
    citas = execute_query(query, (fecha,), fetch_all=True)
    
    if citas:
        # Crear vista de horarios
        horas = list(range(8, 20))  # 8 AM a 8 PM
        
        for hora in horas:
            hora_inicio = datetime.combine(fecha, time(hora, 0))
            hora_fin = hora_inicio + timedelta(hours=1)
            
            citas_hora = [c for c in citas if hora_inicio <= c['fecha_hora_cita'] < hora_fin]
            
            with st.container():
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.write(f"**{hora:02d}:00**")
                with col2:
                    if citas_hora:
                        for cita in citas_hora:
                            estado_color = {
                                'programada': '🔵',
                                'confirmada': '🟢',
                                'en_consulta': '🟡',
                                'completada': '✅',
                                'cancelada': '❌'
                            }.get(cita['estado'], '⚪')
                            
                            st.markdown(
                                f"{estado_color} **{cita['fecha_hora_cita'].strftime('%H:%M')}** - "
                                f"{cita['paciente']} con Dr. {cita['medico']} "
                                f"({cita['especialidad']})"
                            )
                    else:
                        st.write("—")
                st.divider()
    else:
        st.info("No hay citas programadas para esta fecha")

def show_historial_medico():
    """Gestión de historial médico"""
    st.header("Historial Médico")
    
    if not check_permission('ver_historial'):
        st.error("No tiene permisos para ver historiales médicos")
        return
    
    # Buscar paciente
    busqueda_paciente = st.text_input("🔍 Buscar Paciente", placeholder="Nombre o documento...")
    
    if busqueda_paciente:
        pacientes = buscar_pacientes(busqueda_paciente)
        
        if pacientes:
            paciente_seleccionado = st.selectbox(
                "Seleccionar Paciente",
                options=[p['id'] for p in pacientes],
                format_func=lambda x: next(p['nombre'] for p in pacientes if p['id'] == x)
            )
            
            if paciente_seleccionado:
                mostrar_historial_paciente(paciente_seleccionado)
        else:
            st.info("No se encontraron pacientes")
    else:
        # Si hay cita activa, mostrar directamente
        if 'cita_activa' in st.session_state:
            cita_info = get_cita_info(st.session_state['cita_activa'])
            if cita_info:
                st.info(f"Atendiendo cita: {cita_info['paciente']} - {cita_info['fecha_hora']}")
                mostrar_historial_paciente(cita_info['id_paciente'])
                if st.button("❌ Finalizar Atención"):
                    del st.session_state['cita_activa']
                    st.rerun()

def mostrar_historial_paciente(paciente_id):
    """Muestra el historial completo de un paciente"""
    
    # Información del paciente
    paciente_info = get_paciente_info(paciente_id)
    if paciente_info:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nombre", paciente_info['nombre'])
        with col2:
            st.metric("Edad", paciente_info['edad'])
        with col3:
            st.metric("Teléfono", paciente_info['telefono'] or "—")
    
    # Tabs para diferentes secciones
    tab1, tab2, tab3 = st.tabs(["📋 Historial Clínico", "➕ Nueva Atención", "📊 Resumen"])
    
    with tab1:
        # Historial de atenciones
        query = """
            SELECT 
                h.fecha_atencion,
                u.nombre_completo as medico,
                e.nombre_especialidad as especialidad,
                h.diagnostico,
                h.tratamiento,
                h.receta,
                h.signos_vitales
            FROM historial_medico h
            JOIN medicos m ON h.id_medico = m.id
            JOIN usuarios u ON m.id = u.id
            JOIN especialidades e ON m.id_especialidad = e.id
            WHERE h.id_paciente = %s
            ORDER BY h.fecha_atencion DESC
        """
        historial = execute_query(query, (paciente_id,), fetch_all=True)
        
        if historial:
            for registro in historial:
                with st.expander(f"📅 {format_datetime(registro['fecha_atencion'])} - Dr. {registro['medico']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Diagnóstico:**")
                        st.write(registro['diagnostico'])
                        st.markdown("**Tratamiento:**")
                        st.write(registro['tratamiento'] or "—")
                    with col2:
                        st.markdown("**Receta:**")
                        st.write(registro['receta'] or "—")
                        if registro['signos_vitales']:
                            st.markdown("**Signos Vitales:**")
                            vitales = parse_json_field(registro['signos_vitales'])
                            for key, value in vitales.items():
                                st.write(f"• {key}: {value}")
        else:
            st.info("El paciente no tiene historial médico previo")
    
    with tab2:
        # Nueva atención médica
        if check_permission('atender_citas'):
            with st.form("form_atencion"):
                st.subheader("Registrar Nueva Atención")
                
                # Si hay cita activa, mostrar información
                cita_activa_id = st.session_state.get('cita_activa')
                if cita_activa_id:
                    cita_info = get_cita_info(cita_activa_id)
                    st.info(f"Cita: {cita_info['fecha_hora']} - Dr. {cita_info['medico']}")
                    medico_id = cita_info['id_medico']
                else:
                    # Seleccionar médico
                    medicos = get_medicos_activos()
                    medico_id = st.selectbox(
                        "Médico*",
                        options=medicos['id'].tolist(),
                        format_func=lambda x: medicos[medicos['id'] == x]['nombre'].iloc[0]
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    diagnostico = st.text_area("Diagnóstico*", height=100)
                    tratamiento = st.text_area("Tratamiento", height=100)
                with col2:
                    receta = st.text_area("Receta", height=100)
                    notas = st.text_area("Notas de Evolución", height=100)
                
                st.subheader("Signos Vitales")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    presion = st.text_input("Presión Arterial", placeholder="120/80")
                with col2:
                    temperatura = st.number_input("Temperatura (°C)", min_value=35.0, max_value=42.0, step=0.1)
                with col3:
                    peso = st.number_input("Peso (kg)", min_value=0.0, max_value=300.0, step=0.1)
                with col4:
                    altura = st.number_input("Altura (m)", min_value=0.5, max_value=2.5, step=0.01)
                
                submit = st.form_submit_button("💾 Guardar Atención", use_container_width=True)
                
                if submit:
                    if not diagnostico:
                        st.error("El diagnóstico es obligatorio")
                    else:
                        signos_vitales = {
                            "presion": presion,
                            "temperatura": temperatura,
                            "peso": peso,
                            "altura": altura
                        }
                        
                        registrar_atencion(
                            paciente_id, medico_id, cita_activa_id,
                            diagnostico, tratamiento, receta, notas,
                            signos_vitales
                        )
    
    with tab3:
        # Resumen estadístico del paciente
        mostrar_resumen_paciente(paciente_id)

def registrar_atencion(paciente_id, medico_id, cita_id, diagnostico, tratamiento, receta, notas, signos_vitales):
    """Registra una nueva atención médica"""
    try:
        query = """
            INSERT INTO historial_medico 
            (id_paciente, id_medico, id_cita, diagnostico, tratamiento, 
             receta, notas_evolucion, signos_vitales, usuario_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        execute_query(
            query,
            (paciente_id, medico_id, cita_id, diagnostico, tratamiento,
             receta, notas, signos_vitales, st.session_state.username),
            commit=True
        )
        
        # Actualizar estado de la cita
        if cita_id:
            actualizar_estado_cita(cita_id, 'completada')
            if 'cita_activa' in st.session_state:
                del st.session_state['cita_activa']
        
        st.success("Atención registrada exitosamente")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error al registrar la atención: {str(e)}")

def mostrar_resumen_paciente(paciente_id):
    """Muestra resumen estadístico del paciente"""
    
    # Total de consultas
    query_total = """
        SELECT 
            COUNT(*) as total_consultas,
            COUNT(DISTINCT EXTRACT(YEAR FROM fecha_atencion)) as años_atencion,
            MIN(fecha_atencion) as primera_consulta,
            MAX(fecha_atencion) as ultima_consulta
        FROM historial_medico
        WHERE id_paciente = %s
    """
    stats = execute_query(query_total, (paciente_id,), fetch_one=True)
    
    if stats and stats['total_consultas'] > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Consultas", stats['total_consultas'])
        with col2:
            st.metric("Años en seguimiento", stats['años_atencion'] or 0)
        with col3:
            st.metric("Primera Consulta", format_date(stats['primera_consulta']))
        with col4:
            st.metric("Última Consulta", format_date(stats['ultima_consulta']))
        
        # Diagnósticos más frecuentes
        query_diagnosticos = """
            SELECT 
                diagnostico,
                COUNT(*) as frecuencia
            FROM historial_medico
            WHERE id_paciente = %s
            GROUP BY diagnostico
            ORDER BY frecuencia DESC
            LIMIT 5
        """
        diagnosticos = execute_query(query_diagnosticos, (paciente_id,), fetch_all=True)
        
        if diagnosticos:
            st.subheader("Diagnósticos Frecuentes")
            df_diag = pd.DataFrame(diagnosticos)
            st.dataframe(df_diag, use_container_width=True, hide_index=True)

def show_facturacion():
    """Módulo de facturación"""
    st.header("Facturación")
    
    if not check_permission('generar_reportes'):
        st.error("No tiene permisos para ver facturación")
        return
    
    # Tabs para facturación
    tab1, tab2 = st.tabs(["💰 Facturas Pendientes", "📊 Reporte de Facturación"])
    
    with tab1:
        mostrar_facturas_pendientes()
    
    with tab2:
        reporte_facturacion()

def mostrar_facturas_pendientes():
    """Muestra facturas pendientes de pago"""
    
    query = """
        SELECT 
            f.id,
            f.numero_factura,
            u.nombre_completo as paciente,
            f.fecha_emision,
            f.monto_total,
            f.metodo_pago,
            f.estado_pago,
            c.fecha_hora_cita as fecha_cita
        FROM facturas f
        JOIN pacientes p ON f.id_paciente = p.id
        JOIN usuarios u ON p.id = u.id
        LEFT JOIN citas c ON f.id_cita = c.id
        WHERE f.estado_pago = 'pendiente'
        ORDER BY f.fecha_emision
    """
    facturas = execute_query(query, fetch_all=True)
    
    if facturas:
        total_pendiente = sum(f['monto_total'] for f in facturas)
        
        st.metric("Total Pendiente", f"${total_pendiente:,.2f}")
        st.divider()
        
        for factura in facturas:
            col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2, 1.5, 1.5, 1.5, 1])
            
            with col1:
                st.write(f"**{factura['numero_factura']}**")
            with col2:
                st.write(factura['paciente'])
            with col3:
                st.write(format_date(factura['fecha_emision']))
            with col4:
                st.write(f"${factura['monto_total']:,.2f}")
            with col5:
                metodo = factura['metodo_pago'] or "Pendiente"
                st.write(metodo)
            with col6:
                if st.button("💳 Pagar", key=f"pay_{factura['id']}"):
                    procesar_pago(factura['id'])
            
            st.divider()
    else:
        st.success("✅ No hay facturas pendientes")

def procesar_pago(factura_id):
    """Procesa el pago de una factura"""
    try:
        query = """
            UPDATE facturas 
            SET estado_pago = 'pagado',
                fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id = %s
        """
        execute_query(query, (st.session_state.username, factura_id), commit=True)
        
        st.success("Pago registrado exitosamente")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error al procesar el pago: {str(e)}")

def reporte_facturacion():
    """Genera reporte de facturación por período"""
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_desde = st.date_input("Desde", value=datetime.now().replace(day=1))
    with col2:
        fecha_hasta = st.date_input("Hasta", value=datetime.now())
    
    if st.button("📊 Generar Reporte", use_container_width=True):
        query = """
            SELECT 
                DATE(fecha_emision) as fecha,
                COUNT(*) as total_facturas,
                SUM(CASE WHEN estado_pago = 'pagado' THEN monto_total ELSE 0 END) as pagado,
                SUM(CASE WHEN estado_pago = 'pendiente' THEN monto_total ELSE 0 END) as pendiente,
                COUNT(CASE WHEN estado_pago = 'pagado' THEN 1 END) as facturas_pagadas,
                COUNT(CASE WHEN estado_pago = 'pendiente' THEN 1 END) as facturas_pendientes
            FROM facturas
            WHERE DATE(fecha_emision) BETWEEN %s AND %s
            GROUP BY DATE(fecha_emision)
            ORDER BY fecha
        """
        reporte = execute_query(query, (fecha_desde, fecha_hasta), fetch_all=True)
        
        if reporte:
            df = pd.DataFrame(reporte)
            
            # Totales
            total_facturas = df['total_facturas'].sum()
            total_pagado = df['pagado'].sum()
            total_pendiente = df['pendiente'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Facturas", total_facturas)
            with col2:
                st.metric("Total Pagado", f"${total_pagado:,.2f}")
            with col3:
                st.metric("Total Pendiente", f"${total_pendiente:,.2f}")
            
            st.divider()
            
            # Detalle por día
            st.dataframe(
                df,
                column_config={
                    "fecha": "Fecha",
                    "total_facturas": "Facturas",
                    "pagado": st.column_config.NumberColumn("Pagado", format="$%.2f"),
                    "pendiente": st.column_config.NumberColumn("Pendiente", format="$%.2f"),
                    "facturas_pagadas": "Pagadas",
                    "facturas_pendientes": "Pendientes"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay facturas en el período seleccionado")

# Funciones auxiliares
def get_pacientes_activos():
    """Obtiene pacientes activos para select"""
    query = """
        SELECT p.id, u.nombre_completo as nombre
        FROM pacientes p
        JOIN usuarios u ON p.id = u.id
        WHERE u.activo = true
        ORDER BY u.nombre_completo
    """
    result = execute_query(query, fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def get_medicos_activos():
    """Obtiene médicos activos para select"""
    query = """
        SELECT m.id, u.nombre_completo as nombre
        FROM medicos m
        JOIN usuarios u ON m.id = u.id
        WHERE u.activo = true
        ORDER BY u.nombre_completo
    """
    result = execute_query(query, fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def get_especialidades_activas():
    """Obtiene especialidades activas para select"""
    query = "SELECT id, nombre_especialidad as nombre FROM especialidades WHERE activo = true ORDER BY nombre_especialidad"
    result = execute_query(query, fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def get_medicos_por_especialidad(especialidad_id):
    """Obtiene médicos por especialidad"""
    query = """
        SELECT m.id, u.nombre_completo as nombre
        FROM medicos m
        JOIN usuarios u ON m.id = u.id
        WHERE m.id_especialidad = %s AND u.activo = true
        ORDER BY u.nombre_completo
    """
    result = execute_query(query, (especialidad_id,), fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def get_consultorios_activos():
    """Obtiene consultorios activos"""
    query = "SELECT id, nombre FROM consultorios WHERE activo = true ORDER BY nombre"
    result = execute_query(query, fetch_all=True)
    return pd.DataFrame(result) if result else pd.DataFrame()

def get_citas_con_filtros(desde, hasta, estado, medico):
    """Obtiene citas con filtros aplicados"""
    query = """
        SELECT 
            c.id,
            c.fecha_hora_cita,
            u_pac.nombre_completo as paciente,
            u_med.nombre_completo as medico,
            e.nombre_especialidad as especialidad,
            c.estado,
            c.motivo_consulta
        FROM citas c
        JOIN pacientes p ON c.id_paciente = p.id
        JOIN usuarios u_pac ON p.id = u_pac.id
        JOIN medicos m ON c.id_medico = m.id
        JOIN usuarios u_med ON m.id = u_med.id
        JOIN especialidades e ON m.id_especialidad = e.id
        WHERE DATE(c.fecha_hora_cita) BETWEEN %s AND %s
    """
    params = [desde, hasta]
    
    if estado != "todas":
        query += " AND c.estado = %s"
        params.append(estado)
    
    if medico != "todos":
        query += " AND u_med.nombre_completo = %s"
        params.append(medico)
    
    query += " ORDER BY c.fecha_hora_cita"
    
    return execute_query(query, tuple(params), fetch_all=True)

def actualizar_estado_cita(cita_id, nuevo_estado):
    """Actualiza el estado de una cita"""
    try:
        query = """
            UPDATE citas 
            SET estado = %s,
                fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id = %s
        """
        execute_query(query, (nuevo_estado, st.session_state.username, cita_id), commit=True)
        st.rerun()
    except Exception as e:
        st.error(f"Error al actualizar estado: {str(e)}")

def get_cita_info(cita_id):
    """Obtiene información detallada de una cita"""
    query = """
        SELECT 
            c.id,
            c.id_paciente,
            c.id_medico,
            u_pac.nombre_completo as paciente,
            u_med.nombre_completo as medico,
            c.fecha_hora_cita
        FROM citas c
        JOIN pacientes p ON c.id_paciente = p.id
        JOIN usuarios u_pac ON p.id = u_pac.id
        JOIN medicos m ON c.id_medico = m.id
        JOIN usuarios u_med ON m.id = u_med.id
        WHERE c.id = %s
    """
    return execute_query(query, (cita_id,), fetch_one=True)

def get_paciente_info(paciente_id):
    """Obtiene información detallada de un paciente"""
    query = """
        SELECT 
            u.nombre_completo as nombre,
            EXTRACT(YEAR FROM AGE(p.fecha_nacimiento)) as edad,
            p.telefono,
            p.direccion
        FROM pacientes p
        JOIN usuarios u ON p.id = u.id
        WHERE p.id = %s
    """
    return execute_query(query, (paciente_id,), fetch_one=True)

def buscar_pacientes(termino):
    """Busca pacientes por nombre"""
    query = """
        SELECT p.id, u.nombre_completo as nombre
        FROM pacientes p
        JOIN usuarios u ON p.id = u.id
        WHERE u.nombre_completo ILIKE %s
        ORDER BY u.nombre_completo
        LIMIT 10
    """
    return execute_query(query, (f"%{termino}%",), fetch_all=True)

def get_medicos_lista():
    """Obtiene lista de médicos para filtros"""
    query = """
        SELECT DISTINCT u.nombre_completo as nombre
        FROM medicos m
        JOIN usuarios u ON m.id = u.id
        WHERE u.activo = true
        ORDER BY u.nombre_completo
    """
    return execute_query(query, fetch_all=True)
