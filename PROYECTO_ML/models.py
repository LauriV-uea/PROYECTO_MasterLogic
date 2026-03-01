# Clase producto
# Representa cada producto del inventario usando POO

class Producto:
    def __init__(self, id_producto, nombre, cantidad, precio):

        #atributos privados del producto
        self.__id_producto = id_producto
        self.__nombre = nombre
        self.__cantidad = cantidad
        self.__precio = precio


    # Getters
    #permiten obtener el valor de los atributos
    def get_id(self):
        return self.__id_producto

    def get_nombre(self):
        return self.__nombre

    def get_cantidad(self):
        return self.__cantidad

    def get_precio(self):
        return self.__precio


    #Setters
    # permiten modificar el valor de los atributos
    def set_cantidad(self, nueva_cantidad):
        self.__cantidad = nueva_cantidad

    def set_precio(self, nueva_precio):
        self.__precio = nueva_precio