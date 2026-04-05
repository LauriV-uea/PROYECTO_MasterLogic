from database import get_connection


def obtener_conexion():
    """
    Devuelve una conexión MySQL usando la config de database._config().
    Se usa el wrapper que permite placeholders estilo '?'.
    """
    return get_connection()
