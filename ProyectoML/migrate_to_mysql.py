"""
Herramienta para migrar los datos del SQLite local (`masterlogic.db`)
al esquema MySQL usado por la app (por defecto la base `servicios`).

Requisitos previos:
1) Tener MySQL levantado (XAMPP/MAMP/WAMP) y credenciales con permiso de crear BD.
2) Variables de entorno opcionales:
   - MYSQL_HOST (default 127.0.0.1)
   - MYSQL_PORT (default 3306)
   - MYSQL_USER (default root)
   - MYSQL_PASSWORD (default "")
   - MYSQL_DB (default servicios)

Uso desde PowerShell:
    python migrate_to_mysql.py
"""

import sqlite3
import pymysql

from ProyectoML.database import _config, init_db


SQLITE_PATH = "masterlogic.db"


def _get(row, key, default=None):
    return row[key] if key in row.keys() else default


def ensure_database_exists(cfg: dict) -> None:
    """Crea la base de datos destino si no existe."""
    server_conn = pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        autocommit=True,
    )
    with server_conn.cursor() as cur:
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}` "
            "DEFAULT CHARACTER SET utf8mb4"
        )
    server_conn.close()


def copy_table(sqlite_conn, mysql_conn, table, mapping):
    """
    Copia datos de una tabla SQLite a MySQL.

    mapping: dict {dest_col: src_col|callable|None}
    """
    rows = sqlite_conn.execute(f"SELECT * FROM {table}").fetchall()
    if not rows:
        return 0

    dest_cols = list(mapping.keys())
    placeholders = ", ".join(["%s"] * len(dest_cols))
    insert_sql = f"INSERT INTO {table} ({', '.join(dest_cols)}) VALUES ({placeholders})"

    payload = []
    for row in rows:
        item = []
        for _, src in mapping.items():
            if callable(src):
                item.append(src(row))
            elif src is None:
                item.append(None)
            else:
                item.append(row[src])
        payload.append(tuple(item))

    with mysql_conn.cursor() as cur:
        cur.executemany(insert_sql, payload)
    return len(payload)


def migrate():
    cfg = _config()

    # 1) Crear BD y tablas en MySQL
    ensure_database_exists(cfg)
    init_db()

    # 2) Conexiones
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    mysql_conn = pymysql.connect(**cfg)

    try:
        with mysql_conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Limpiar destino (orden seguro)
        for tbl in [
            "factura_detalle",
            "servicio_repuesto",
            "facturas",
            "servicios",
            "repuestos",
            "productos",
            "tecnicos",
            "clientes",
            "usuarios",
        ]:
            with mysql_conn.cursor() as cur:
                cur.execute(f"DELETE FROM {tbl}")

        # Migraciones
        copied = {}
        copied["clientes"] = copy_table(
            sqlite_conn,
            mysql_conn,
            "clientes",
            {
                "id": "id",
                "nombre": "nombre",
                "apellidos": "apellidos",
                "correo": "correo",
                "telefono": "telefono",
                "direccion": "direccion",
                "dni": "dni",
                "estado": (lambda _: "Activo"),
            },
        )

        copied["tecnicos"] = copy_table(
            sqlite_conn,
            mysql_conn,
            "tecnicos",
            {
                "id": "id",
                "nombre": "nombre",
                "especialidad": "especialidad",
                "telefono": (lambda _: None),
                "estado": (lambda _: "Activo"),
            },
        )

        copied["productos"] = copy_table(
            sqlite_conn,
            mysql_conn,
            "productos",
            {
                "id": "id",
                "nombre": "nombre",
                "descripcion": (lambda r: _get(r, "descripcion")),
                "cantidad": "cantidad",
                "precio": "precio",
                "id_cliente": (lambda r: _get(r, "id_cliente")),
                "estado": (lambda _: "Activo"),
            },
        )

        copied["servicios"] = copy_table(
            sqlite_conn,
            mysql_conn,
            "servicios",
            {
                "id": "id",
                "descripcion": "descripcion",
                "costo": "costo",
                "id_cliente": (lambda r: _get(r, "id_cliente")),
                "tecnico": (lambda r: _get(r, "tecnico")),
                "especialidad": (lambda r: _get(r, "especialidad")),
                "fecha_solicitud": (lambda r: _get(r, "fecha_solicitud")),
                "estado": (lambda r: _get(r, "estado", "Activo")),
            },
        )

        copied["repuestos"] = copy_table(
            sqlite_conn,
            mysql_conn,
            "repuestos",
            {
                "id": "id",
                "nombre": "nombre",
                "descripcion": (lambda _: None),
                "precio": "precio",
                "cantidad": "cantidad",
                "id_cliente": (lambda r: _get(r, "id_cliente")),
                "estado": (lambda _: "Activo"),
            },
        )

        copied["servicio_repuesto"] = copy_table(
            sqlite_conn,
            mysql_conn,
            "servicio_repuesto",
            {
                "id_servicio": "id_servicio",
                "id_repuesto": "id_repuesto",
                "cantidad": (lambda _: 1),
            },
        )

        copied["facturas"] = copy_table(
            sqlite_conn,
            mysql_conn,
            "facturas",
            {
                "id": "id",
                "id_cliente": "id_cliente",
                "numero_factura": (lambda _: None),
                "fecha": (lambda r: _get(r, "fecha")),
                "total": "total",
                "estado": (lambda r: _get(r, "estado", "Pendiente")),
            },
        )

        copied["factura_detalle"] = copy_table(
            sqlite_conn,
            mysql_conn,
            "factura_detalle",
            {
                "id": "id",
                "id_factura": "id_factura",
                "concepto": "concepto",
                "cantidad": "cantidad",
                "precio_unitario": "precio_unitario",
                "subtotal": "subtotal",
            },
        )

        copied["usuarios"] = copy_table(
            sqlite_conn,
            mysql_conn,
            "usuarios",
            {
                "id": "id",
                "usuario": "usuario",
                "email": "email",
                "password": "password",
                "nombre": "nombre",
                "estado": (lambda r: _get(r, "estado", "Activo")),
            },
        )

        with mysql_conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")

        mysql_conn.commit()
    finally:
        mysql_conn.close()
        sqlite_conn.close()

    print("Migración completada:")
    for table, count in copied.items():
        print(f" - {table}: {count} filas")


if __name__ == "__main__":
    migrate()
