

import sqlite3

#función  para conectar con la base de datos SQlite
def conectar():
    return sqlite3.connect('inventario.db')

# Función para crear la tabla de productos si no existe
def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio REAL NOT NULL
    )
    """)

    conexion.commit()
    conexion.close()
