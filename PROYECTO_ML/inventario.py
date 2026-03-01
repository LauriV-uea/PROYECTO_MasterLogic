
from models import Producto

#Clase inventario,
# maneja la coleeción de los productos mediante un diccioanrio
class Inventario:
    def __init__(self):
        # Diccionario para almacenar productos
        #clave= ID del producto
        # valor = objeto del producto
        self.productos ={}


    #añadir producto al
    def agregar_producto(self, producto):
        self.productos[producto.get_id()] = producto


    #eliminar producto por ID
    def eliminar_producto(self, id_producto):
        if id_producto in self.productos:
            del self.productos[id_producto]


    # actualizar cantidad o precio
    def actualizar_producto(self, id_producto, cantidad=None, precio=None):
        if id_producto in self.productos:
            if cantidad is not None:
                self.productos[id_producto].set_cantidad(cantidad)
            if precio is not None:
                self.productos[id_producto].set_precio(precio)

    #buscar productos por nombre
    def buscar_producto(self, nombre):
        return [p for p in self.productos.values() if p.get_nombre() == nombre]

    # mostrar todos los productos
    def mostar_producto(self, nombre):
        return list(self.productos.values())



