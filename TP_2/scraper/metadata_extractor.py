
"""
Módulo para extraer metadatos (links y meta tags)
de un documento HTML usando BeautifulSoup.
"""

from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin

def extract_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """
    Extrae todos los enlaces (href) de las etiquetas <a> y
    los convierte en URLs absolutas.

    Args:
        soup (BeautifulSoup): Objeto BeautifulSoup del HTML parseado.
        base_url (str): La URL base de la página para resolver links relativos.

    Returns:
        List[str]: Lista de URLs absolutas encontradas.
    """
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href']
        if href and not href.startswith('#') and not href.startswith('mailto:'):
            # Convertir URL relativa en absoluta
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
    return list(set(links)) # Devuelve solo links únicos

def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extrae meta tags relevantes: description, keywords, y Open Graph (og:).

    Args:
        soup (BeautifulSoup): Objeto BeautifulSoup del HTML parseado.

    Returns:
        Dict[str, str]: Diccionario con los meta tags encontrados.
    """
    meta_tags = {}
    
    desc = soup.find("meta", attrs={"name": "description"})
    if desc and desc.get("content"):
        meta_tags["description"] = desc["content"]
        
    keywords = soup.find("meta", attrs={"name": "keywords"})
    if keywords and keywords.get("content"):
        meta_tags["keywords"] = keywords["content"]

    og_tags = soup.find_all("meta", attrs={"property": lambda x: x and x.startswith('og:')})
    for tag in og_tags:
        if tag.get("content"):
            meta_tags[tag["property"]] = tag["content"]
            
    return meta_tags