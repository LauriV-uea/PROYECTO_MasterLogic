from flask import Flask
app = Flask(__name__)
from flask import Flask, render_template, request

app = Flask(__name__)

# ruta principaal
@app.route('/')
def Hola_mundo():
    return "Hola, mundo"


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

if __name__ == '__main__':
    app.run(debug=True)