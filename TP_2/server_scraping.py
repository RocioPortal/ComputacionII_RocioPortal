"""
Implementa el servidor de extracción web asíncrono.
"""

import argparse
import asyncio
import sys
import datetime
from urllib.parse import urlparse, ParseResult

from aiohttp import web
import aiohttp
from async_lru import alru_cache
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup

from scraper import async_http, html_parser, metadata_extractor
from common import protocol

CACHE_TTL = 3600
CACHE_MAX_SIZE = 128
RATE_LIMIT_PER_MINUTE = 10
RATE_LIMIT_INTERVAL = 60
# ------------------------------

TASK_TIMEOUT_SECONDS = 70 


async def setup_background_tasks(app: web.Application):
    """Función de 'startup' para aiohttp."""
    app['http_session'] = aiohttp.ClientSession(
        headers={'User-Agent': 'TP2-ComputacionII-Scraper/1.0'}
    )
    print("Sesión aiohttp.ClientSession creada.")
    
async def cleanup_background_tasks(app: web.Application):
    """Función de 'cleanup' para aiohttp."""
    await app['http_session'].close()
    print("Sesión aiohttp.ClientSession cerrada.")


def get_domain_limiter(app: web.Application, url: str) -> AsyncLimiter:
    """Obtiene o crea un Rate Limiter para el dominio de la URL."""
    try:
        domain: str = urlparse(url).netloc
        if not domain:
            domain = url.split('/')[0]
    except Exception:
        domain = "default"

    if domain not in app['domain_limiters']:
        print(f"[RateLimit] Creando nuevo limiter para dominio: {domain}")
        app['domain_limiters'][domain] = AsyncLimiter(
            RATE_LIMIT_PER_MINUTE, RATE_LIMIT_INTERVAL
        )
    return app['domain_limiters'][domain]


@alru_cache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TTL)
async def perform_full_analysis(app: web.Application, url: str) -> dict:
    """
    Función principal de trabajo, envuelta por el decorador de caché.
    """
    print(f"[Cache] MISS para {url}. Ejecutando análisis completo.")
    
    limiter = get_domain_limiter(app, url)
    semaphore = app['scraper_semaphore']
    
    async with limiter:
        print(f"[RateLimit] Adquiriendo permiso para {url}")
        async with semaphore:
            print(f"[Semaphore] Adquiriendo worker para {url}")
            
            # --- 1. Scraping (Parte A) ---
            html_content = await async_http.fetch_page(app['http_session'], url)
            
            if html_content is None:
                raise Exception(f"No se pudo obtener el contenido HTML de {url}")

            soup = BeautifulSoup(html_content, 'lxml')
            
            structure_data = html_parser.parse_html_structure(soup)
            links = metadata_extractor.extract_links(soup, url)
            meta_tags = metadata_extractor.extract_meta_tags(soup)
            
            scraping_data = {
                "title": structure_data['title'],
                "links": links,
                "meta_tags": meta_tags,
                "structure": structure_data['structure'],
                "images_count": structure_data['images_count']
            }
            
            # --- 2. Comunicación (Parte B) ---
            print(f"Contactando al Servidor de Procesamiento para {url}...")
            proc_host = app['config']['proc_host']
            proc_port = app['config']['proc_port']
            
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(proc_host, proc_port),
                timeout=10.0
            )
            
            print(f"Conectado a Servidor B. Enviando tarea: {url}")
            
            request_to_b = {
                "url": url,
                "html_content": html_content
            }
            
            await protocol.async_send_msg(writer, request_to_b)
            
            response_from_b = await asyncio.wait_for(
                protocol.async_read_msg(reader),
                timeout=TASK_TIMEOUT_SECONDS + 10 
            )
            
            print(f"Respuesta recibida de Servidor B para {url}")
            writer.close()
            await writer.wait_closed()
            
            if response_from_b.get('status') != 'success':
                raise Exception(f"Servidor B falló: {response_from_b.get('message', 'Error desconocido')}")
            
            processing_data = response_from_b.get('data', {})

            # --- 3. Consolidar Respuesta ---
            final_result = {
                "url": url,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "scraping_data": scraping_data,
                "processing_data": processing_data,
                "status": "success"
            }
            
            return final_result

async def handle_scrape_request(request: web.Request):
    """
    Manejador de la ruta POST /scrape.
    Punto de entrada para el cliente.
    """
    try:
        data = await request.json()
        url = data.get('url')
        
        if not url:
            return web.json_response(
                {"status": "error", "message": "Falta el campo 'url' en el JSON"},
                status=400
            )
        try:
            parsed_url: ParseResult = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                 raise ValueError("Esquema o host inválido")
        except ValueError as e:
            return web.json_response(
                {"status": "error", "message": f"URL inválida: {url} ({e})"},
                status=400
            )

        print(f"Petición recibida para: {url}")
        
        cache_info_before = perform_full_analysis.cache_info()
        hits_before = cache_info_before.hits

        result = await perform_full_analysis(request.app, url)
        
        cache_info_after = perform_full_analysis.cache_info()
        hits_after = cache_info_after.hits

        final_response = result.copy()
        
        if hits_after > hits_before:
            print(f"[Cache] HIT para {url}.")
            final_response["cached"] = True
        else:
            final_response["cached"] = False 

        return web.json_response(final_response, status=200)

    except (asyncio.TimeoutError, ConnectionError) as e:
        print(f"Error de red/timeout comunicando con Servidor B: {e}")
        return web.json_response(
            {"status": "error", "message": f"Error de comunicación con el servidor de procesamiento: {e}"},
            status=504 # Gateway Timeout
        )
    except Exception as e:
        print(f"Error inesperado en 'handle_scrape_request': {e}")
        return web.json_response(
            {"status": "error", "message": f"Error interno del servidor: {str(e)}"},
            status=500
        )

def main():
    
    global TASK_TIMEOUT_SECONDS
    TASK_TIMEOUT_SECONDS = 70 

    parser = argparse.ArgumentParser(
        description="Servidor de Scraping Web Asíncrono (Parte A)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-i', '--ip', required=True, type=str,
        help="Dirección de escucha (soporta IPv4/IPv6)"
    )
    parser.add_argument(
        '-p', '--port', required=True, type=int,
        help="Puerto de escucha"
    )
    parser.add_argument(
        '-w', '--workers', type=int, default=10,
        help="Número de tareas de scraping concurrentes (default: 10)"
    )
    parser.add_argument(
        '--proc-host', required=True, type=str,
        help="Host del Servidor de Procesamiento (Parte B)"
    )
    parser.add_argument(
        '--proc-port', required=True, type=int,
        help="Puerto del Servidor de Procesamiento (Parte B)"
    )
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()

    app = web.Application()
    
    app['config'] = {
        'proc_host': args.proc_host,
        'proc_port': args.proc_port
    }
    app['domain_limiters'] = {}
    app['scraper_semaphore'] = asyncio.Semaphore(args.workers)

    app.router.add_post('/scrape', handle_scrape_request)
    
    app.on_startup.append(setup_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    print(f"Iniciando Servidor de Scraping en http://{args.ip}:{args.port}")
    print(f"Conectando a Servidor de Procesamiento en {args.proc_host}:{args.proc_port}")
    print(f"Límite de workers (semáforo): {args.workers}")
    print(f"Caché: HABILITADA (TTL={CACHE_TTL}s, MaxSize={CACHE_MAX_SIZE})") # <-- HABILITADA
    print(f"Rate Limiting: Habilitado (Max={RATE_LIMIT_PER_MINUTE}/min por dominio)")

    try:
        web.run_app(app, host=args.ip, port=args.port)
    except OSError as e:
        print(f"\nError: No se pudo iniciar el servidor en {args.ip}:{args.port}. ¿El puerto ya está en uso?")
        print(f"Detalle: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCerrando servidor (Ctrl+C)...")
    finally:
        print("Servidor de Scraping detenido.")

if __name__ == "__main__":
    main()