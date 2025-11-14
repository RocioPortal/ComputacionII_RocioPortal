#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TP2 - tests/test_metadata_extractor.py

Test unitario para el módulo scraper.metadata_extractor
"""

import pytest
from bs4 import BeautifulSoup
from scraper.metadata_extractor import extract_links, extract_meta_tags

@pytest.fixture
def sample_soup() -> BeautifulSoup:
    """Fixture que devuelve un objeto BeautifulSoup de un HTML de prueba."""
    html_doc = """
    <html>
    <head>
        <meta name="description" content="Descripción de prueba">
        <meta property="og:title" content="Título OG">
    </head>
    <body>
        <a href="https://www.google.com">Link Absoluto</a>
        <a href="/pagina-relativa">Link Relativo</a>
        <a href="otra-pagina.html">Link Relativo 2</a>
        <a href="#ancla">Link de Ancla (ignorar)</a>
        <a href="mailto:test@test.com">Mail (ignorar)</a>
        <a href="https://www.google.com">Link Absoluto (duplicado)</a>
    </body>
    </html>
    """
    return BeautifulSoup(html_doc, 'lxml')

def test_extract_links(sample_soup: BeautifulSoup):
    """
    Testea la función extract_links.
    Verifica que convierta links relativos a absolutos y
    que ignore anclas y mailto.
    """
    base_url = "https://example.com/inicio/"
    
    # 1. Ejecutar la función
    links = extract_links(sample_soup, base_url)
    
    # 2. Verificar los resultados (Asserts)
    
    # Debería haber 3 links únicos
    assert len(links) == 3
    
    # Verificar que los links estén correctos y sean absolutos
    assert "https://www.google.com" in links
    
    # **** ¡AQUÍ ESTÁ LA CORRECCIÓN! ****
    # El link relativo con / va a la raíz, no a /inicio/
    assert "https://example.com/pagina-relativa" in links
    assert "https://example.com/inicio/otra-pagina.html" in links
    
    # Verificar que ignoró los links no deseados
    assert "https://example.com/inicio/#ancla" not in links
    assert "mailto:test@test.com" not in links

def test_extract_meta_tags(sample_soup: BeautifulSoup):
    """Testea la extracción de meta tags."""
    
    # 1. Ejecutar la función
    meta = extract_meta_tags(sample_soup)

    # 2. Verificar los resultados (Asserts)
    assert len(meta) == 2
    assert meta["description"] == "Descripción de prueba"
    assert meta["og:title"] == "Título OG"