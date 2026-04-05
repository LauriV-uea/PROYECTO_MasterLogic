import sys
print("Python path:", sys.path[:3])

print("\n1. Importing flask_wtf...")
try:
    from flask_wtf import FlaskForm
    print("   OK")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

print("2. Importing wtforms...")
try:
    from wtforms import StringField, IntegerField, FloatField, SubmitField
    print("   OK")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

print("3. Importing wtforms.validators...")
try:
    from wtforms.validators import DataRequired
    print("   OK")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

print("\n4. Defining class...")
try:
    class ProductoForm(FlaskForm):
        nombre = StringField("Nombre", validators=[DataRequired()])
        cantidad = IntegerField("Cantidad", validators=[DataRequired()])
        precio = FloatField("Precio", validators=[DataRequired()])
        submit = SubmitField("Guardar")
    print("   OK - ProductoForm defined")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n5. Checking if ProductoForm is in globals...")
print("   ProductoForm exists:", 'ProductoForm' in globals())

print("\nSUCCESS!")
