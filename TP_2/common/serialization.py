
import json

def serialize(data: dict) -> bytes:
    """
    Serializa un diccionario a bytes (JSON con encoding UTF-8).

    Args:
        data (dict): El diccionario a serializar.

    Returns:
        bytes: Los datos serializados.
    """
    try:
        return json.dumps(data).encode('utf-8')
    except (TypeError, OverflowError) as e:
        # Maneja casos donde los datos no son serializables por JSON
        print(f"Error de serialización: {e}")
        # Retorna un JSON de error como fallback
        error_data = {"error": "Datos no serializables", "details": str(e)}
        return json.dumps(error_data).encode('utf-8')

def deserialize(raw_data: bytes) -> dict:
    """
    Deserializa bytes (JSON con encoding UTF-8) a un diccionario.

    Args:
        raw_data (bytes): Los datos crudos recibidos (ej: del socket).

    Returns:
        dict: El diccionario deserializado.
    """
    try:
        return json.loads(raw_data.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        # Maneja casos de JSON mal formado o encoding incorrecto
        print(f"Error de deserialización: {e}")
        return {"error": "Datos corruptos o mal formados", "raw": raw_data[:100]}