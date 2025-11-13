"""
Cliente de prueba para el sistema de Scraping.
Envía una petición POST /scrape al Servidor A (asyncio)
y espera la respuesta JSON consolidada.
"""

import argparse
import asyncio
import aiohttp
import json
import sys
import time

async def main():
    
    parser = argparse.ArgumentParser(
        description="Cliente de prueba para el Servidor de Scraping"
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        type=str,
        help="Host del Servidor de Scraping (Parte A)"
    )
    parser.add_argument(
        '--port',
        default=8000,
        type=int,
        help="Puerto del Servidor de Scraping (Parte A)"
    )
    parser.add_argument(
        '--url',
        required=True,
        type=str,
        help="URL que se debe analizar (ej: https://example.com)"
    )
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    if ':' in args.host: 
        base_url = f"http://[{args.host}]:{args.port}"

    api_endpoint = f"{base_url}/scrape"
    payload = {"url": args.url}
    
    print(f"Contactando al servidor en: {api_endpoint}")
    print(f"Enviando URL para analizar: {args.url}")
    print("Esperando respuesta consolidada...")
    
    start_time = time.time()
    
    try:
        timeout = aiohttp.ClientTimeout(total=120.0) 
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(api_endpoint, json=payload) as response:
                
                end_time = time.time()
                print(f"\n--- Respuesta recibida en {end_time - start_time:.2f} segundos ---")
                
                try:
                    data = await response.json()
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    if response.status != 200:
                         print(f"\nADVERTENCIA: El servidor devolvió un código de error: {response.status}")
                         
                except aiohttp.ContentTypeError:
                    print(f"Error: El servidor devolvió una respuesta no-JSON (Código: {response.status})")
                    print(await response.text())
                    
    except aiohttp.ClientConnectionError as e:
        print(f"\nError: No se pudo conectar al servidor en {base_url}.")
        print(f"Detalle: {e}")
        print("Asegúrate de que 'server_scraping.py' esté corriendo en esa dirección.")
    except asyncio.TimeoutError:
        print(f"\nError: Timeout. El servidor tardó más de 120 segundos en responder.")
    except Exception as e:
        print(f"\nError inesperado del cliente: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")