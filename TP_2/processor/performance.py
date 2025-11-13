"""
Módulo de procesamiento (Parte B) para analizar el rendimiento de carga
de una página web usando Playwright. (Versión corregida)
"""

import time
from playwright.sync_api import sync_playwright, Error, TimeoutError
from typing import Dict, Any, List

def analyze_performance(url: str) -> Dict[str, Any]:
    """
    Analiza el rendimiento de carga de una URL.
    Calcula:
    - Tiempo de carga (load_time_ms)
    - Número de peticiones (num_requests)
    - Tamaño total (total_size_kb)

    Args:
        url (str): La URL a analizar.

    Returns:
        Dict[str, Any]: Diccionario con los datos de rendimiento.
    """
    print(f"[Processor] Analizando rendimiento de: {url}")
    
    network_requests: List[Dict] = []

    def on_response(response):
        """
        Callback para capturar CADA respuesta de red.
        ¡Nueva lógica! Leemos el body() directamente.
        """
        size = 0
        try:
            body = response.body()
            size = len(body)
            
            network_requests.append({
                "url": response.url,
                "status": response.status,
                "size": size
            })
            
        except Exception as e:
            # Esto es NORMAL para peticiones que no tienen body
            # (como redirecciones 301 o 304).
            # Igual la contamos como una petición de tamaño 0.
            network_requests.append({
                "url": response.url,
                "status": response.status,
                "size": 0
            })
            # Imprimimos una nota en la Terminal 1
            print(f"  [Info performance.py] Petición sin body (Status {response.status}).")


    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Registrar el callback 'response'
            page.on("response", on_response)
            
            start_time = time.time()
            
            # Ir a la URL, esperar a que la red esté inactiva
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            load_time_ms = int((time.time() - start_time) * 1000)
            
            browser.close()
            
            # Calcular totales
            total_size_bytes = sum(req['size'] for req in network_requests)
            total_size_kb = round(total_size_bytes / 1024, 2)
            num_requests = len(network_requests)
            
            return {
                "load_time_ms": load_time_ms,
                "total_size_kb": total_size_kb,
                "num_requests": num_requests
            }
            
    except TimeoutError:
        print(f"Error [Performance]: Timeout al cargar {url}")
        return {"error": "Timeout"}
    except Error as e:
        print(f"Error [Performance]: Fallo Playwright para {url}: {e}")
        return {"error": f"Fallo Playwright: {e}"}
    except Exception as e:
        print(f"Error [Performance]: Fallo inesperado para {url}: {e}")
        return {"error": f"Fallo inesperado: {e}"}