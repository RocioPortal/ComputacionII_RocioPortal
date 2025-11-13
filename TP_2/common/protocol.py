
"""
Define el protocolo de comunicación por sockets entre el Servidor A y B.
Se utiliza un protocolo simple:
1. Header de 4 bytes: Un entero (unsigned long long) que indica
   la longitud del mensaje JSON.
2. Payload: El mensaje JSON (serializado) de esa longitud.

Provee versiones asíncronas (para Servidor A) y síncronas (para Servidor B).
"""

import asyncio
import socket
import struct
from .serialization import serialize, deserialize

# Formato del header: Unsigned Long Long (8 bytes)
# Usar 'Q' (8 bytes) es más robusto para mensajes grandes que 'L' (4 bytes)
HEADER_FORMAT = '!Q'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# --- Versiones Asíncronas (para Servidor A / asyncio) ---

async def async_send_msg(writer: asyncio.StreamWriter, msg_dict: dict):
    """
    (Asíncrono) Serializa un dict, crea un header con la longitud
    y envía ambos por el asyncio.StreamWriter.
    """
    serialized_msg = serialize(msg_dict)
    header = struct.pack(HEADER_FORMAT, len(serialized_msg))
    
    try:
        writer.write(header)
        await writer.drain()
        
        writer.write(serialized_msg)
        await writer.drain()
    except (ConnectionError, BrokenPipeError) as e:
        print(f"Error de conexión al enviar mensaje: {e}")
        raise

async def async_read_msg(reader: asyncio.StreamReader) -> dict:
    """
    (Asíncrono) Lee el header de 8 bytes, determina la longitud
    y luego lee esa cantidad de bytes del asyncio.StreamReader.
    Deserializa el resultado a un dict.
    """
    try:
        header_data = await reader.readexactly(HEADER_SIZE)
        if not header_data:
            raise ConnectionError("La conexión se cerró (leyendo header)")
            
        msg_len = struct.unpack(HEADER_FORMAT, header_data)[0]
        
        # Lee el payload completo
        payload_data = await reader.readexactly(msg_len)
        if not payload_data:
            raise ConnectionError("La conexión se cerró (leyendo payload)")

        return deserialize(payload_data)
        
    except asyncio.IncompleteReadError as e:
        print(f"Error de lectura incompleta: {e}")
        raise ConnectionError("Lectura incompleta desde el socket")
    except (ConnectionError, BrokenPipeError) as e:
        print(f"Error de conexión al leer mensaje: {e}")
        raise

# --- Versiones Síncronas (para Servidor B / socketserver) ---

def blocking_send_msg(sock: socket.socket, msg_dict: dict):
    """
    (Síncrono) Serializa, empaqueta y envía un mensaje por un socket
    estándar (bloqueante).
    """
    serialized_msg = serialize(msg_dict)
    header = struct.pack(HEADER_FORMAT, len(serialized_msg))
    
    try:
        sock.sendall(header)
        sock.sendall(serialized_msg)
    except (ConnectionError, BrokenPipeError) as e:
        print(f"Error de conexión al enviar mensaje (bloqueante): {e}")
        raise

def _blocking_read_n(sock: socket.socket, n: int) -> bytes:
    """Helper para leer exactamente n bytes de un socket bloqueante."""
    chunks = []
    bytes_recd = 0
    while bytes_recd < n:
        chunk = sock.recv(min(n - bytes_recd, 4096))
        if chunk == b'':
            raise ConnectionError("Socket cerrado inesperadamente")
        chunks.append(chunk)
        bytes_recd += len(chunk)
    return b''.join(chunks)

def blocking_read_msg(sock: socket.socket) -> dict:
    """
    (Síncrono) Lee el header y el payload desde un socket
    estándar (bloqueante).
    """
    try:
        header_data = _blocking_read_n(sock, HEADER_SIZE)
        msg_len = struct.unpack(HEADER_FORMAT, header_data)[0]
        
        payload_data = _blocking_read_n(sock, msg_len)
        
        return deserialize(payload_data)
        
    except (ConnectionError, BrokenPipeError) as e:
        print(f"Error de conexión al leer mensaje (bloqueante): {e}")
        raise