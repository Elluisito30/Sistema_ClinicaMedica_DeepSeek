import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import streamlit as st
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class DatabasePool:
    _instance = None
    _connection_pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        """Inicializa el pool de conexiones"""
        try:
            self._connection_pool = psycopg2.pool.SimpleConnectionPool(
                1,  # Mínimo de conexiones
                20,  # Máximo de conexiones
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'db_clinica'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )
            logger.info("Pool de conexiones inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando pool de conexiones: {e}")
            st.error("Error de conexión a la base de datos")
            raise

    def get_connection(self):
        """Obtiene una conexión del pool"""
        try:
            return self._connection_pool.getconn()
        except Exception as e:
            logger.error(f"Error obteniendo conexión del pool: {e}")
            return None

    def return_connection(self, conn):
        """Retorna una conexión al pool"""
        try:
            self._connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error retornando conexión al pool: {e}")

    def close_all_connections(self):
        """Cierra todas las conexiones del pool"""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("Todas las conexiones cerradas")

# Función helper para ejecutar consultas
def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Ejecuta una consulta SQL y maneja la conexión automáticamente
    """
    db_pool = DatabasePool()
    conn = None
    cursor = None
    
    try:
        conn = db_pool.get_connection()
        if not conn:
            raise Exception("No se pudo obtener conexión de la base de datos")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params or ())
        
        result = None
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        if commit:
            conn.commit()
            
        return result
        
    except Exception as e:
        if conn and commit:
            conn.rollback()
        logger.error(f"Error ejecutando consulta: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            db_pool.return_connection(conn)

def test_connection():
    """Prueba la conexión a la base de datos"""
    try:
        result = execute_query("SELECT 1 as test", fetch_one=True)
        return result is not None
    except Exception as e:
        logger.error(f"Error en test de conexión: {e}")
        return False