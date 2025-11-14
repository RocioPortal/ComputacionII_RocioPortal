"""
Test unitario para el módulo scraper.html_parser
"""

import pytest
from bs4 import BeautifulSoup
from scraper.html_parser import parse_html_structure

@pytest.fixture
def sample_soup() -> BeautifulSoup:
    html_doc = """
    <html>
    <head>
        <title>Título de Prueba</title>
    </head>
    <body>
        <h1>Encabezado Principal</h1>
        <p>Un párrafo.</p>
        <img src="img1.jpg">
        <img src="img2.png">
        <h1>Otro Encabezado Principal</h1>
        <h2>Un Subtítulo</h2>
    </body>
    </html>
    """
    return BeautifulSoup(html_doc, 'lxml')

def test_parse_html_structure_full(sample_soup: BeautifulSoup):
    """
    Testea la función parse_html_structure con un HTML completo.
    Verifica que el título, la estructura de 'h1'/'h2' y 
    el conteo de imágenes sean correctos.
    """
    # 1. Ejecutar la función a testear
    data = parse_html_structure(sample_soup)

    # 2. Verificar los resultados (Asserts)
    assert data["title"] == "Título de Prueba"
    assert data["images_count"] == 2
    assert data["structure"]["h1"] == 2
    assert data["structure"]["h2"] == 1
    assert data["structure"]["h3"] == 0 # Verificar un caso 0

def test_parse_html_structure_no_title():
    """Testea qué pasa si el HTML no tiene etiqueta <title>."""
    html_doc = "<html><body><h1>Hola</h1></body></html>"
    soup = BeautifulSoup(html_doc, 'lxml')
    
    data = parse_html_structure(soup)
    
    assert data["title"] == "Sin título"
    assert data["structure"]["h1"] == 1