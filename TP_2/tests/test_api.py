#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TP2 - tests/test_api.py

(Bonus) Test de integración simple para el endpoint /scrape.
NOTA: Este test asume que AMBOS servidores (Parte A y B)
están corriendo en sus puertos default (8000 y 9000) en localhost.
"""

import pytest
import aiohttp
import asyncio

# Configuración del test
SCRAPER_HOST = "127.0.0.1"
SCRAPER_PORT = 8000
TEST_URL = "https://example.com" # Usar una URL simple y rápida

BASE_URL = f"http://{SCRAPER_HOST}:{SCRAPER_PORT}"

@pytest.mark.asyncio
async def test_scrape_endpoint_success():
    """
    Testea el endpoint /scrape con una URL válida (example.com).
    Verifica que la respuesta sea 200, tenga el status 'success'
    y contenga las claves esperadas.
    """
    print(f"Ejecutando test contra {BASE_URL}. Asegúrate de que los servidores A y B estén corriendo.")
    
    timeout = aiohttp.ClientTimeout(total=60.0) 
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            payload = {"url": TEST_URL}
            
            async with session.post(f"{BASE_URL}/scrape", json=payload) as response:
                
                assert response.status == 200
                
                data = await response.json()
                
                # Verificar estructura general
                assert "status" in data
                assert data["status"] == "success"
                assert data["url"] == TEST_URL
                assert "timestamp" in data
                
                # Verificar datos de Scraping (Parte A)
                assert "scraping_data" in data
                scraping_data = data["scraping_data"]
                assert scraping_data["title"] == "Example Domain"
                assert "links" in scraping_data
                assert "meta_tags" in scraping_data
                assert "structure" in scraping_data
                assert scraping_data["structure"]["h1"] >= 1
                
                # Verificar datos de Procesamiento (Parte B)
                assert "processing_data" in data
                processing_data = data["processing_data"]
                assert "screenshot" in processing_data
                assert "performance" in processing_data
                assert "thumbnails" in processing_data
                
                # Verificar que los datos no estén vacíos
                assert processing_data["screenshot"] is not None
                assert processing_data["performance"]["load_time_ms"] > 0
                
                print(f"Test exitoso para {TEST_URL}. (Cacheado: {data.get('cached', 'N/A')})")

    except aiohttp.ClientConnectionError:
        pytest.skip(f"Test de integración omitido: No se pudo conectar a {BASE_URL}. ¿Servidores están corriendo?")
    except asyncio.TimeoutError:
        pytest.fail("Timeout durante el test. El servidor tardó demasiado.")