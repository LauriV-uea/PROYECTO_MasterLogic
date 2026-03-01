
from flask import Flask, render_template, request, redirect
from inventario import Inventario
from models import Producto
from database import conectar, crear_tabla
import os
crear_tabla()
inventario = Inventario()

app = Flask(__name__)

# ruta principaal
@app.route('/')
def index():
    return render_template('index.html')

# Registro de clientes
@app.route('/register', methods=['GET', 'POST'])
def register_client():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        correo = request.form['correo']
        dni = request.form['dni']
        # Aquí se guardaría en la base de datos
        return f"Cliente {nombre} registrado con éxito."
    return render_template('register_client.html')

# Solicitud de asistencia técnica
@app.route('/service', methods=['GET', 'POST'])
def service_request():
    if request.method == 'POST':
        servicio_id = request.form['servicio_id']
        fecha = request.form['fecha']
        tipo = request.form['tipo']
        estado = request.form['estado']
        tecnico = request.form['tecnico']
        especialidad = request.form['especialidad']
        # Aquí se guardaría en la base de datos
        return f"Solicitud {servicio_id} registrada correctamente."
    return render_template('service_request.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/inventario', methods=['GET', 'POST'])
def inventario_view():
    #si el usuario enva el formulario(agregar producto)
    if request.method == 'POST':
        id_producto = request.form['id']
        nombre  = request.form['nombre']
        cantidad = request.form['cantidad']
        precio = float(request.form['precio'])

        # Crear objeto Producto (POO)
        producto = Producto(id_producto, nombre, cantidad, precio)


        # Agregar al diccionario (colección)
        inventario.agregar_producto(producto)

        # Guardar en SQlite
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO productos VALUES (?, ?, ?, ?)",
        (id_producto, nombre, cantidad, precio))
        conexion.commit()
        conexion.close()


    # mostrar todos los productos almacenados en la base de datos
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conexion.close()

    return render_template( 'inventario.html', productos=productos)



@app.route('/eliminar', methods=['POST'])
def eliminar_producto():
    id_producto = int(request.form['id'])

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
    conexion.commit()
    conexion.close()

    return redirect('/inventario')

@app.route('/buscar')
def buscar_producto():
    nombre = request.args.get('nombre')

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos WHERE nombre = ?", (nombre,))
    productos = cursor.fetchall()
    conexion.close()

    return render_template('inventario.html', productos=productos)

@app.route("/actualizar", methods=["POST"])
def actualizar_producto():
    conexion = conectar()
    cursor = conexion.cursor()

    id = request.form["id"]
    cantidad = request.form["cantidad"]
    precio = request.form["precio"]

    cursor.execute("""
        UPDATE productos
        SET cantidad = ?, precio = ?
        WHERE id = ?
    """, (cantidad, precio, id))

    conexion.commit()
    conexion.close()

    return redirect("/inventario")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


