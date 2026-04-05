from .bd import obtener_conexion

def obtener_clientes():

    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes")

    clientes = cursor.fetchall()

    conn.close()

    return clientes