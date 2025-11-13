# Rocio Portal
# Legajo: 63217

---

# TP2 - Sistema de Scraping y Análisis Web Distribuido

Este proyecto implementa un sistema distribuido de scraping y análisis web en Python, como parte del Trabajo Práctico N°2 de la materia Computación II.

El sistema se divide en dos componentes principales:
1.  **Servidor de Extracción (Parte A)**: Un servidor asíncrono (`asyncio` + `aiohttp`) que recibe peticiones HTTP, realiza el scraping inicial y coordina con el servidor de procesamiento.
2.  **Servidor de Procesamiento (Parte B)**: Un servidor (`multiprocessing` + `socketserver`) que maneja tareas pesadas (CPU-bound) como tomar screenshots y analizar rendimiento, utilizando un pool de procesos.

## 🚀 Características Implementadas

* **Parte A (Asyncio)**: Servidor HTTP no bloqueante con `aiohttp`.
* **Parte B (Multiprocessing)**: Servidor TCP con `socketserver` y `ProcessPoolExecutor` para paralelismo real.
* **Comunicación**: Sockets TCP con un protocolo simple (header de longitud + JSON) para la comunicación entre servidores.
* **Soporte de Red**: Capacidad para escuchar en **IPv4** (`127.0.0.1`) e **IPv6** (`::1`).
* **Funcionalidad Mínima**:
    1.  Scraping de contenido HTML (título, links).
    2.  Extracción de metadatos (meta tags, estructura de headers).
    3.  Generación de screenshot (usando Playwright).
    4.  Análisis de rendimiento (usando Playwright).
    5.  Procesamiento de imágenes (thumbnails).
* **Manejo de Errores**: Timeouts, errores de red y excepciones de procesamiento son capturados y reportados.

### 🌟 Bonus Track Implementados
* **Caché en Memoria (TTL 1 hora)**: Los resultados de análisis de una URL se guardan en caché por 1 hora (`async-lru`).
* **Rate Limiting**: Límite de peticiones por dominio (máx 10 por minuto) para no saturar los sitios web (`aiolimiter`).
* **Testing**: Se incluye un test de integración simple en `tests/test_api.py`.

## 🛠️ Instalación y Ejecución (Paso a Paso)

Sigue estos pasos en orden para correr el proyecto.

### Paso 1: Clonar o Descargar

Clona este repositorio o descarga los archivos

### Paso 2: Crear el Entorno Virtual

(Solo necesitas hacerlo una vez)
```bash
# Asegúrate de estar dentro de la carpeta TP_2
python3 -m venv venv
````

### Paso 3: Activar el Entorno Virtual

(Debes hacerlo **cada vez** que abras una nueva terminal para trabajar en el proyecto)

```bash
# En Linux / macOS
source venv/bin/activate
```

```powershell
# En Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

*Tu terminal ahora debería mostrar `(venv)` al principio.*

### Paso 4: Instalar Dependencias de Python

Con el entorno activado, instala todo lo que está en `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Paso 5: Instalar los Navegadores

Playwright necesita descargar los navegadores que usa.

```bash
playwright install
```

### Paso 6: ¡Ejecutar el Sistema\!

Necesitarás **3 terminales abiertas** al mismo tiempo. Asegúrate de que las 3 tengan el entorno virtual activado (Paso 3).

#### ➡️ A. Terminal 1: Servidor de Procesamiento (Parte B)

Inicia el servidor que realiza el trabajo pesado.

```bash
(venv) $ python3 server_processing.py -i 127.0.0.1 -p 9000 -n 4
```

*Verás un mensaje que dice "Iniciando Servidor de Procesamiento...". Déjalo corriendo.*

#### ➡️ B. Terminal 2: Servidor de Scraping (Parte A)

Inicia el servidor principal que recibe al cliente.

```bash
(venv) $ python3 server_scraping.py -i 127.0.0.1 -p 8000 --proc-host 127.0.0.1 --proc-port 9000
```

*Verás un mensaje que dice "Iniciando Servidor de Scraping...". Déjalo corriendo.*

#### ➡️ C. Terminal 3: Cliente de Prueba

¡Es hora de probar\! Envía una URL al Servidor A.

**Prueba 1: (Cache MISS - Lento)**

```bash
(venv) $ python3 client.py --url [https://www.clarin.com/](https://www.clarin.com/) --host 127.0.0.1 --port 8000
```

*Tardará varios segundos (15+) y el resultado dirá `"cached": false`.*

**Prueba 2: (Cache HIT - Rápido)**
Vuelve a ejecutar el mismo comando.

```bash
(venv) $ python3 client.py --url [https://www.clarin.com/](https://www.clarin.com/) --host 127.0.0.1 --port 8000
```

*Será casi instantáneo y el resultado dirá `"cached": true`.*

-----

## 🧪 Testing (Bonus)

Para ejecutar el test de integración automatizado, asegúrate de que ambos servidores (Terminal 1 y 2) sigan corriendo.

Luego, en una **cuarta terminal** (o en la Terminal 3):

```bash
(venv) $ pytest
```

*Deberías ver un mensaje de `== 1 passed ==`.*

## 📖 API

### `POST /scrape`

Envía una URL para ser analizada.

**Request Body (JSON):**

```json
{
  "url": "[https://tu-url.com](https://tu-url.com)"
}
```

```