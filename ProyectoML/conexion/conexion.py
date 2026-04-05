"""Pequeño helper para conectarse a MySQL (XAMPP).

Configura las credenciales vía variables de entorno para no
dejar datos sensibles en el código:
  - MYSQL_HOST (default 127.0.0.1)
  - MYSQL_PORT (default 3306)
  - MYSQL_USER (default root)
  - MYSQL_PASSWORD (default cadena vacía)
  - MYSQL_DB (base de datos a usar, obligatorio)

Ejemplo en Windows (PowerShell):
  setx MYSQL_DB servicios
  setx MYSQL_USER root
  setx MYSQL_PASSWORD ""
"""

import os
import pymysql
from pymysql.cursors import DictCursor


def _config():
    """Arma la configuración tomando valores de entorno."""
    db_name = os.getenv("MYSQL_DB", "servicios")

    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": db_name,
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": False,
    }


def conectar():
    """Devuelve una conexión activa a MySQL."""
    return pymysql.connect(**_config())


def desconectar(conexion):
    """Cierra la conexión a la base de datos."""
    if conexion:
        conexion.close()


def init_mysql_servicios():
    """Crea tablas mínimas (clientes, servicios) si no existen en MySQL."""
    conn = conectar()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS clientes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    apellidos VARCHAR(255),
                    correo VARCHAR(255),
                    telefono VARCHAR(100),
                    direccion VARCHAR(255),
                    dni VARCHAR(100) UNIQUE,
                    estado VARCHAR(50) DEFAULT 'Activo',
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS servicios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    descripcion TEXT NOT NULL,
                    costo DECIMAL(12,2) NOT NULL,
                    id_cliente INT,
                    tecnico VARCHAR(255),
                    especialidad VARCHAR(255),
                    fecha_solicitud DATE,
                    estado VARCHAR(50) DEFAULT 'Activo',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
                )
                """
            )
        conn.commit()
    finally:
        desconectar(conn)
