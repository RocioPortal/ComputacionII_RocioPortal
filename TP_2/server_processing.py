#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TP2 - server_processing.py (Servidor Parte B)

Implementa el servidor de procesamiento distribuido.
Utiliza 'socketserver' para manejar conexiones TCP y 'multiprocessing'
(a través de ProcessPoolExecutor) para ejecutar tareas CPU-bound en paralelo.
"""

import argparse
import socket
import socketserver
import os
import sys
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Optional

from processor import screenshot, performance, image_processor
from common import protocol

TASK_TIMEOUT_SECONDS = 70

class ProcessingRequestHandler(socketserver.BaseRequestHandler):
    """
    Manejador para cada conexión TCP entrante del Servidor A.
    Es instanciado para cada conexión.
    """
    
    def handle(self):
        """
        Maneja la conexión:
        1. Lee el mensaje (dict) del Servidor A.
        2. Envía las tareas al ProcessPoolExecutor.
        3. Espera los resultados.
        4. Envía la respuesta (dict) de vuelta al Servidor A.
        """
        try:
            # 1. Leer el mensaje del Servidor A
            # self.request es el socket de la conexión
            print(f"[ProcessorServer] Conexión recibida de {self.client_address}")
            request_data = protocol.blocking_read_msg(self.request)
            
            url = request_data.get('url')
            html_content = request_data.get('html_content')
            
            if not url or html_content is None:
                raise ValueError("Mensaje inválido, faltan 'url' o 'html_content'")

            print(f"[ProcessorServer] Procesando tareas para: {url}")
            
            # 2. Enviar tareas al Pool de Procesos
            # 'self.server.pool' es el ProcessPoolExecutor global
            pool = self.server.pool
            
            future_ss = pool.submit(screenshot.take_screenshot, url)
            future_perf = pool.submit(performance.analyze_performance, url)
            future_img = pool.submit(image_processor.process_images, url, html_content)

            # 3. Esperar y recolectar resultados
            try:
                ss_result = future_ss.result(timeout=TASK_TIMEOUT_SECONDS)
                perf_result = future_perf.result(timeout=TASK_TIMEOUT_SECONDS)
                img_result = future_img.result(timeout=TASK_TIMEOUT_SECONDS)
                
                response_data = {
                    "status": "success",
                    "data": {
                        "screenshot": ss_result,
                        "performance": perf_result,
                        "thumbnails": img_result
                    }
                }
                
            except FutureTimeoutError:
                print(f"Error: Timeout de {TASK_TIMEOUT_SECONDS}s alcanzado en el pool de procesos para {url}")
                response_data = {"status": "error", "message": "Timeout en el procesamiento"}
                # Cancelar futuros que no terminaron
                future_ss.cancel()
                future_perf.cancel()
                future_img.cancel()

        except (ConnectionError, BrokenPipeError) as e:
            print(f"Error de conexión con el cliente ({self.client_address}): {e}")
            return # No se puede enviar respuesta si la conexión cayó
        except Exception as e:
            print(f"Error crítico en el manejador para {self.client_address}: {e}")
            response_data = {"status": "error", "message": f"Error interno del servidor: {e}"}

        # 4. Enviar respuesta de vuelta al Servidor A
        try:
            protocol.blocking_send_msg(self.request, response_data)
            print(f"[ProcessorServer] Respuesta enviada a {self.client_address}")
        except (ConnectionError, BrokenPipeError) as e:
            print(f"Error: No se pudo enviar la respuesta a {self.client_address}: {e}")
        finally:
            # El 'finally' asegura que la conexión se cierre
            self.request.close()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Un servidor TCP que usa Threads para manejar cada conexión.
    Esto es crucial para que múltiples peticiones de Servidor A
    puedan ser atendidas simultáneamente (mientras esperan
    los resultados del pool de procesos).
    """
    allow_reuse_address = True
    
    def __init__(self, server_address, RequestHandlerClass, pool: ProcessPoolExecutor, bind_and_activate=True, address_family=socket.AF_INET):
        # Configurar la familia de direcciones (IPv4/IPv6)
        self.address_family = address_family
        # Guardar la referencia al pool de procesos
        self.pool = pool
        # Inicializar el TCPServer
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)


def main():
    """Función principal para parsear argumentos y levantar el servidor."""
    
    parser = argparse.ArgumentParser(
        description="Servidor de Procesamiento Distribuido (Parte B)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-i', '--ip',
        required=True,
        type=str,
        help="Dirección de escucha (soporta IPv4 e IPv6)"
    )
    parser.add_argument(
        '-p', '--port',
        required=True,
        type=int,
        help="Puerto de escucha"
    )
    parser.add_argument(
        '-n', '--processes',
        type=int,
        default=os.cpu_count() or 1,
        help="Número de procesos en el pool (default: CPU count)"
    )
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    try:
        addr_info = socket.getaddrinfo(args.ip, args.port, proto=socket.IPPROTO_TCP)
        # Tomar la primera tupla válida
        address_family = addr_info[0][0]
        server_address = addr_info[0][4]
    except socket.gaierror:
        print(f"Error: IP o puerto inválido: {args.ip}:{args.port}")
        sys.exit(1)
        
    if address_family == socket.AF_INET6:
        print("Iniciando en modo IPv6.")
    else:
        print("Iniciando en modo IPv4.")
    # -----------------------------

    num_processes = args.processes
    print(f"Iniciando Servidor de Procesamiento en {server_address}...")
    print(f"Pool de procesos: {num_processes} workers")

    # Crear el Pool de Procesos
    try:
        with ProcessPoolExecutor(max_workers=num_processes) as pool:
            # Iniciar el servidor TCP, pasándole el pool
            with ThreadedTCPServer(
                server_address, 
                ProcessingRequestHandler, 
                pool,
                address_family=address_family
            ) as server:
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    print("\nCerrando servidor (Ctrl+C)...")
                    server.shutdown()
                    print("Servidor cerrado.")
                    
    except Exception as e:
        print(f"Error fatal al iniciar el servidor o el pool: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()