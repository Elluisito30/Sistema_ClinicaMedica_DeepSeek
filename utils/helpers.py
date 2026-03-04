import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import hashlib
import json

def format_date(date_value, format="%d/%m/%Y"):
    """Formatea una fecha"""
    if not date_value:
        return ""
    if isinstance(date_value, str):
        try:
            date_value = datetime.fromisoformat(date_value)
        except:
            return date_value
    return date_value.strftime(format)

def format_datetime(dt_value, format="%d/%m/%Y %H:%M"):
    """Formatea una fecha y hora"""
    if not dt_value:
        return ""
    if isinstance(dt_value, str):
        try:
            dt_value = datetime.fromisoformat(dt_value)
        except:
            return dt_value
    return dt_value.strftime(format)

def format_currency(amount):
    """Formatea un monto como moneda"""
    try:
        return f"${amount:,.2f}"
    except:
        return "$0.00"

def create_bar_chart(data, x, y, title, color=None):
    """Crea un gráfico de barras con Plotly"""
    fig = px.bar(
        data, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        showlegend=True if color else False
    )
    return fig

def create_line_chart(data, x, y, title):
    """Crea un gráfico de líneas con Plotly"""
    fig = px.line(
        data, 
        x=x, 
        y=y, 
        title=title,
        markers=True
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12)
    )
    return fig

def create_pie_chart(data, values, names, title):
    """Crea un gráfico de pastel con Plotly"""
    fig = px.pie(
        data, 
        values=values, 
        names=names, 
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        showlegend=True
    )
    return fig

def generate_id(prefix=""):
    """Genera un ID único"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_hash = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]
    return f"{prefix}{timestamp}{random_hash}"

def parse_json_field(field, default=None):
    """Parsea un campo JSON de manera segura"""
    if not field:
        return default or {}
    if isinstance(field, dict):
        return field
    try:
        return json.loads(field)
    except:
        return default or {}

def get_date_range(period="today"):
    """Obtiene rango de fechas según período"""
    today = datetime.now().date()
    
    if period == "today":
        start_date = today
        end_date = today
    elif period == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == "month":
        start_date = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
    elif period == "year":
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    
    return start_date, end_date

def display_metric_card(label, value, delta=None, help_text=None):
    """Muestra una tarjeta de métrica con estilo mejorado"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div style="
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="color: #666; font-size: 14px;">{label}</div>
                <div style="color: #0066cc; font-size: 32px; font-weight: bold;">{value}</div>
                {f'<div style="color: {"green" if delta>0 else "red"}; font-size: 14px;">{delta}% vs período anterior</div>' if delta else ''}
            </div>
            """,
            unsafe_allow_html=True
        )
        if help_text:
            st.caption(help_text)