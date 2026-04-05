import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from pymysql.cursors import DictCursor


# ---------- Configuración MySQL ----------

def _config():
    db = os.getenv("MYSQL_DB", "servicios")
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": db,
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": False,
    }


class CursorWrapper:
    """Adapta placeholders estilo SQLite (?) a PyMySQL (%s)."""

    def __init__(self, cursor):
        self._cursor = cursor

    def _convert(self, query: str) -> str:
        return query.replace("?", "%s")

    def execute(self, query, params=None):
        return self._cursor.execute(self._convert(query), params)

    def executemany(self, query, params):
        return self._cursor.executemany(self._convert(query), params)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __getattr__(self, item):
        return getattr(self._cursor, item)


class ConnectionWrapper:
    """Wrapper ligero para devolver cursores adaptados."""

    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return CursorWrapper(self._conn.cursor())

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    # Exponer lastrowid si se pide al connection
    @property
    def lastrowid(self):
        return getattr(self._conn, "lastrowid", None)


def get_connection():
    """
    Crea y retorna una conexión a MySQL (phpMyAdmin/XAMPP).
    """
    return ConnectionWrapper(pymysql.connect(**_config()))


# ---------- Inicialización de esquema ----------


def init_db():
    """
    Crea las tablas necesarias para el sistema MasterLogic en MySQL.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Productos
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL UNIQUE,
            descripcion TEXT,
            cantidad INT NOT NULL DEFAULT 0,
            precio DECIMAL(12,2) NOT NULL,
            estado VARCHAR(50) DEFAULT 'Activo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            id_cliente INT
        )
        """
    )

    # Clientes
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

    # Técnicos
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tecnicos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            especialidad VARCHAR(255),
            telefono VARCHAR(100),
            estado VARCHAR(50) DEFAULT 'Activo',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Servicios
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

    # Repuestos
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS repuestos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            descripcion TEXT,
            precio DECIMAL(12,2) NOT NULL,
            cantidad INT NOT NULL DEFAULT 0,
            id_cliente INT,
            estado VARCHAR(50) DEFAULT 'Activo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id)
        )
        """
    )

    # Relación servicio-repuesto
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS servicio_repuesto (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_servicio INT NOT NULL,
            id_repuesto INT NOT NULL,
            cantidad INT DEFAULT 1,
            FOREIGN KEY (id_servicio) REFERENCES servicios(id),
            FOREIGN KEY (id_repuesto) REFERENCES repuestos(id)
        )
        """
    )

    # Facturas
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS facturas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_cliente INT NOT NULL,
            numero_factura VARCHAR(255) UNIQUE,
            fecha DATE DEFAULT CURRENT_DATE,
            total DECIMAL(12,2) NOT NULL,
            estado VARCHAR(50) DEFAULT 'Pendiente',
            FOREIGN KEY (id_cliente) REFERENCES clientes(id)
        )
        """
    )

    # Detalles de factura
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS factura_detalle (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_factura INT NOT NULL,
            concepto TEXT NOT NULL,
            cantidad DECIMAL(12,2),
            precio_unitario DECIMAL(12,2),
            subtotal DECIMAL(12,2),
            FOREIGN KEY (id_factura) REFERENCES facturas(id)
        )
        """
    )

    # Usuarios
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            nombre VARCHAR(255),
            estado VARCHAR(50) DEFAULT 'Activo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Índices útiles
    cur.execute("CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_clientes_dni ON clientes(dni)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_repuestos_nombre ON repuestos(nombre)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tecnicos_nombre ON tecnicos(nombre)")

    conn.commit()
    conn.close()


# ============= FUNCIONES DE BÚSQUEDA =============


def buscar_productos(termino):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM productos
        WHERE nombre LIKE ? OR descripcion LIKE ?
        ORDER BY nombre
        """,
        (f"%{termino}%", f"%{termino}%"),
    )
    resultados = cursor.fetchall()
    conn.close()
    return resultados


def buscar_clientes(termino):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM clientes
        WHERE nombre LIKE ? OR correo LIKE ? OR telefono LIKE ? OR dni LIKE ?
        ORDER BY nombre
        """,
        (f"%{termino}%", f"%{termino}%", f"%{termino}%", f"%{termino}%"),
    )
    resultados = cursor.fetchall()
    conn.close()
    return resultados


def buscar_clientes_exacto(nombre=None, correo=None, dni=None):
    conn = get_connection()
    cursor = conn.cursor()

    condiciones = []
    parametros = []

    if nombre:
        condiciones.append("nombre LIKE ?")
        parametros.append(f"%{nombre}%")
    if correo:
        condiciones.append("correo LIKE ?")
        parametros.append(f"%{correo}%")
    if dni:
        condiciones.append("dni = ?")
        parametros.append(dni)

    if not condiciones:
        return []

    query = "SELECT * FROM clientes WHERE " + " AND ".join(condiciones) + " ORDER BY nombre"
    cursor.execute(query, tuple(parametros))
    resultados = cursor.fetchall()
    conn.close()
    return resultados


def buscar_repuestos(termino):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM repuestos
        WHERE nombre LIKE ? OR descripcion LIKE ?
        ORDER BY nombre
        """,
        (f"%{termino}%", f"%{termino}%"),
    )
    resultados = cursor.fetchall()
    conn.close()
    return resultados


def buscar_tecnicos(termino):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM tecnicos
        WHERE nombre LIKE ? OR especialidad LIKE ?
        ORDER BY nombre
        """,
        (f"%{termino}%", f"%{termino}%"),
    )
    resultados = cursor.fetchall()
    conn.close()
    return resultados


def buscar_global(termino):
    conn = get_connection()
    cursor = conn.cursor()

    resultados = {
        "productos": [],
        "clientes": [],
        "repuestos": [],
        "tecnicos": [],
        "servicios": [],
    }

    if termino.strip():
        busqueda = f"%{termino}%"

        cursor.execute(
            """
            SELECT 'producto' as tipo, id, nombre, null as correo, null as precio_unitario,
                   precio, cantidad, null as especialidad FROM productos
            WHERE nombre LIKE ? OR descripcion LIKE ?
            """,
            (busqueda, busqueda),
        )
        resultados["productos"] = cursor.fetchall()

        cursor.execute(
            """
            SELECT 'cliente' as tipo, id, nombre, correo, telefono as precio_unitario,
                   null as precio, null as cantidad, null as especialidad FROM clientes
            WHERE nombre LIKE ? OR correo LIKE ? OR telefono LIKE ? OR dni LIKE ?
            """,
            (busqueda, busqueda, busqueda, busqueda),
        )
        resultados["clientes"] = cursor.fetchall()

        cursor.execute(
            """
            SELECT 'repuesto' as tipo, id, nombre, null as correo, null as precio_unitario,
                   precio, cantidad, null as especialidad FROM repuestos
            WHERE nombre LIKE ? OR descripcion LIKE ?
            """,
            (busqueda, busqueda),
        )
        resultados["repuestos"] = cursor.fetchall()

        cursor.execute(
            """
            SELECT 'tecnico' as tipo, id, nombre, null as correo, null as precio_unitario,
                   null as precio, null as cantidad, especialidad FROM tecnicos
            WHERE nombre LIKE ? OR especialidad LIKE ?
            """,
            (busqueda, busqueda),
        )
        resultados["tecnicos"] = cursor.fetchall()

        cursor.execute(
            """
            SELECT 'servicio' as tipo, id, descripcion as nombre, null as correo, null as precio_unitario,
                   costo as precio, null as cantidad, null as especialidad FROM servicios
            WHERE descripcion LIKE ?
            """,
            (busqueda,),
        )
        resultados["servicios"] = cursor.fetchall()

    conn.close()
    return resultados


# ============= FUNCIONES DE AUTENTICACIÓN =============


def crear_usuario(usuario, email, password, nombre=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO usuarios(usuario, email, password, nombre)
            VALUES (?, ?, ?, ?)
            """,
            (usuario, email, password_hash, nombre),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def verificar_usuario(usuario_email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE usuario = ? OR email = ?",
        (usuario_email, usuario_email),
    )
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return user
    return None
