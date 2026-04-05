#!/usr/bin/env python
# Script para crear un usuario de prueba
from database import crear_usuario

# Crear usuario de prueba
resultado = crear_usuario("admin", "admin@masterlogic.com", "admin123", "Administrador")

if resultado:
    print("✅ Usuario de prueba creado exitosamente!")
    print("Usuario: admin")
    print("Contraseña: admin123")
    print("Email: admin@masterlogic.com")
else:
    print("❌ El usuario ya existe o hubo un error")
