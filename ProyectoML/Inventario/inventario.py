from ProyectoML.database import get_connection as obtener_conexion
from productos import obtener_productos, agregar_producto, eliminar_producto, actualizar_producto, Producto

class Inventario:
    def __init__(self):
        self.productos = {}

    def agregar_producto(self, nombre, cantidad, precio):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
                       (nombre, cantidad, precio))
        conn.commit()
        conn.close()

def mostrar_productos():
    productos = obtener_productos()
    for producto in productos:
        print(Producto(producto["id"], producto["nombre"], producto["cantidad"], producto["precio"]))  

def main():
    while True:
        print("\nInventario de Productos")
        print("1. Mostrar productos")
        print("2. Agregar producto")
        print("3. Eliminar producto")
        print("4. Actualizar producto")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            mostrar_productos()
        elif opcion == "2":
            nombre = input("Nombre del producto: ")
            cantidad = int(input("Cantidad: "))
            precio = float(input("Precio: "))
            agregar_producto(nombre, cantidad, precio)
            print("Producto agregado.")
        elif opcion == "3":
            id = int(input("ID del producto a eliminar: "))
            eliminar_producto(id)
            print("Producto eliminado.")
        elif opcion == "4":
            id = int(input("ID del producto a actualizar: "))
            nombre = input("Nuevo nombre del producto: ")
            cantidad = int(input("Nueva cantidad: "))
            precio = float(input("Nuevo precio: "))
            actualizar_producto(id, nombre, cantidad, precio)
            print("Producto actualizado.")
        elif opcion == "5":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__": 
    main()

