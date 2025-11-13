"""
Módulo de procesamiento (Parte B) para generar screenshots de páginas web
usando Playwright.
"""

import base64
from playwright.sync_api import sync_playwright, Error, TimeoutError
from typing import Optional

def take_screenshot(url: str) -> Optional[str]:
    """
    Toma una captura de pantalla (PNG) de una URL usando Playwright
    en modo headless.

    Args:
        url (str): La URL a capturar.

    Returns:
        Optional[str]: La imagen PNG codificada en base64, o None si falla.
    """
    print(f"[Processor] Tomando screenshot de: {url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Ir a la URL, esperar a que la red esté inactiva (networkidle)
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Tomar screenshot
            screenshot_bytes = page.screenshot(type="png", full_page=True)
            
            browser.close()
            
            # Codificar en base64
            return base64.b64encode(screenshot_bytes).decode('utf-8')
            
    except TimeoutError:
        print(f"Error [Screenshot]: Timeout al cargar la página {url}")
        return None
    except Error as e:
        print(f"Error [Screenshot]: Fallo Playwright para {url}: {e}")
        return None
    except Exception as e:
        print(f"Error [Screenshot]: Fallo inesperado para {url}: {e}")
        return None