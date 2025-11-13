"""
Módulo para extraer información estructural básica de un documento HTML
usando BeautifulSoup.
"""

from bs4 import BeautifulSoup
from typing import Dict

def parse_html_structure(soup: BeautifulSoup) -> Dict:
    """
    Extrae el título de la página y la estructura de encabezados (H1-H6).

    Args:
        soup (BeautifulSoup): Objeto BeautifulSoup del HTML parseado.

    Returns:
        dict: Un diccionario con 'title' y 'structure'.
    """
    
    title = soup.title.string.strip() if soup.title else "Sin título"
    
    header_counts = {
        "h1": len(soup.find_all("h1")),
        "h2": len(soup.find_all("h2")),
        "h3": len(soup.find_all("h3")),
        "h4": len(soup.find_all("h4")),
        "h5": len(soup.find_all("h5")),
        "h6": len(soup.find_all("h6")),
    }
    
    images_count = len(soup.find_all("img"))

    return {
        "title": title,
        "structure": header_counts,
        "images_count": images_count
    }