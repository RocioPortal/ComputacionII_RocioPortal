"""
Módulo de procesamiento (Parte B) para descargar las imágenes principales
y generar thumbnails.
"""

import base64
import requests
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Optional

# Límite de thumbnails a generar
MAX_THUMBNAILS = 5
THUMBNAIL_SIZE = (100, 100) # (width, height)

def process_images(url: str, html_content: str) -> List[str]:
    """
    Extrae las primeras N imágenes del HTML, las descarga y genera
    thumbnails codificados en base64.

    Args:
        url (str): La URL base (para resolver links relativos).
        html_content (str): El contenido HTML de la página (obtenido por Server A).

    Returns:
        List[str]: Lista de strings base64 (PNG) de los thumbnails.
    """
    print(f"[Processor] Procesando imágenes de: {url}")
    
    if not html_content:
        return []

    try:
        soup = BeautifulSoup(html_content, 'lxml')
    except Exception as e:
        print(f"Error [Images]: Fallo al parsear HTML para {url}: {e}")
        return []

    image_urls = []
    for img_tag in soup.find_all("img", src=True):
        src = img_tag['src']
        if src and not src.startswith('data:'): # Ignorar imágenes inline
            full_url = urljoin(url, src)
            image_urls.append(full_url)
    
    unique_urls = list(dict.fromkeys(image_urls))[:MAX_THUMBNAILS]
    
    thumbnails_b64 = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for img_url in unique_urls:
        thumb = _download_and_resize(img_url, headers)
        if thumb:
            thumbnails_b64.append(thumb)
            
    return thumbnails_b64

def _download_and_resize(img_url: str, headers: dict) -> Optional[str]:
    """
    Helper: Descarga una imagen, la redimensiona y la devuelve como base64.
    (Esta es una operación bloqueante, perfecta para el process pool)
    """
    try:
        # Usar 'requests' (bloqueante)
        response = requests.get(img_url, timeout=10, headers=headers, stream=True)
        response.raise_for_status()
        
        # Leer el contenido en memoria
        image_data = BytesIO(response.content)
        
        with Image.open(image_data) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            img.thumbnail(THUMBNAIL_SIZE)
            
            # Guardar en memoria
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            
            # Codificar
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
            
    except requests.exceptions.RequestException as e:
        print(f"Error [Images]: Fallo al descargar {img_url}: {e}")
        return None
    except UnidentifiedImageError:
        print(f"Error [Images]: No se pudo identificar formato de imagen en {img_url}")
        return None
    except Exception as e:
        print(f"Error [Images]: Fallo inesperado al procesar {img_url}: {e}")
        return None