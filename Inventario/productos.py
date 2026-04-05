from .bd import obtener_conexion


def obtener_productos():
    """
    Devuelve todos los productos usando MySQL.
    Usa cursor() porque el wrapper de conexión no expone execute directo.
    """
    conexion = obtener_conexion()
    cur = conexion.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    conexion.close()
    return productos


def agregar_producto(nombre, cantidad, precio):
    conexion = obtener_conexion()
    cur = conexion.cursor()
    cur.execute(
        "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
        (nombre, cantidad, precio),
    )
    conexion.commit()
    conexion.close()


def eliminar_producto(id):
    conexion = obtener_conexion()
    cur = conexion.cursor()
    cur.execute(
        "DELETE FROM productos WHERE id = ?",
        (id,),
    )
    conexion.commit()
    conexion.close()


def actualizar_producto(id, nombre, cantidad, precio):
    conexion = obtener_conexion()
    cur = conexion.cursor()
    cur.execute(
        "UPDATE productos SET nombre = ?, cantidad = ?, precio = ? WHERE id = ?",
        (nombre, cantidad, precio, id),
    )
    conexion.commit()
    conexion.close()

class Producto:
    def __init__(self, producto_id, nombre, cantidad, precio):
        self.producto_id = producto_id
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    def __str__(self):
        return f"ID: {self.producto_id}, Nombre: {self.nombre}, Cantidad: {self.cantidad}, Precio: {self.precio}"

