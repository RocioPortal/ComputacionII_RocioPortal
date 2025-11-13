"""
Módulo para realizar peticiones HTTP asíncronas usando aiohttp.
"""

import asyncio
import aiohttp
from typing import Optional

# Timeout global para las peticiones de scraping
SCRAPE_TIMEOUT_SECONDS = 30

async def fetch_page(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    """
    Realiza una petición GET asíncrona a una URL y devuelve
    el contenido HTML como texto.

    Maneja timeouts y errores comunes de aiohttp.

    Args:
        session (aiohttp.ClientSession): La sesión de cliente aiohttp.
        url (str): La URL a la que hacer fetch.

    Returns:
        Optional[str]: El contenido HTML de la página, o None si falla.
    """
    print(f"[Scraper] Haciendo fetch de: {url}")
    timeout = aiohttp.ClientTimeout(total=SCRAPE_TIMEOUT_SECONDS)
    try:
        async with session.get(url, timeout=timeout, allow_redirects=True) as response:
            # Asegurarse de que la respuesta sea exitosa (2xx)
            response.raise_for_status()
            
            # Asegurarse de que sea HTML
            if 'text/html' not in response.content_type:
                print(f"Error: El contenido no es text/html ({response.content_type})")
                return None
                
            # Leer el contenido
            # Usar read() y luego decode (en lugar de text()) da más
            # control sobre errores de encoding, aunque text() suele ser
            # suficiente y maneja el charset de la respuesta.
            # Por simplicidad y robustez, usaremos text().
            return await response.text()
            
    except asyncio.TimeoutError:
        print(f"Error: Timeout de {SCRAPE_TIMEOUT_SECONDS}s alcanzado para {url}")
        return None
    except aiohttp.ClientResponseError as e:
        print(f"Error de respuesta HTTP: {e.status} {e.message} para {url}")
        return None
    except aiohttp.ClientConnectionError as e:
        print(f"Error de conexión: {e} para {url}")
        return None
    except aiohttp.InvalidURL as e:
        print(f"Error: URL inválida: {e} para {url}")
        return None
    except Exception as e:
        print(f"Error inesperado durante el fetch de {url}: {e}")
        return None