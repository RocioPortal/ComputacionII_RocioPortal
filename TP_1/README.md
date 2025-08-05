# Sistema Concurrente de Análisis Biométrico con Blockchain

Sistema concurrente en Python que simula, procesa y almacena datos biométricos en una cadena de bloques local, utilizando `multiprocessing` para el análisis en paralelo.

---
## Arquitectura

- **Proceso Principal:** Genera 1 muestra/segundo de datos biométricos y la distribuye a los analizadores vía `Pipes`.
- **Procesos Analizadores (x3):** Cada uno se especializa en una métrica (frecuencia, presión, oxígeno), calcula estadísticas sobre una ventana móvil y envía el resultado a una `Queue` compartida.
- **Proceso Verificador:** Consolida los resultados, valida los datos, construye los bloques y los persiste en `blockchain.json`.

---
## Uso

Se recomienda utilizar un entorno virtual.

1.  **Crear y activar entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install numpy
    ```

3.  **Ejecutar la simulación (60 seg):**
    Este comando genera el archivo `blockchain.json`.
    ```bash
    python3 sistema_biometrico.py
    ```

4.  **Verificar la cadena y generar el reporte:**
    Este comando lee `blockchain.json` y crea `reporte.txt`.
    ```bash
    python3 verificar_cadena.py
    ```

---
## Archivos Generados

- `blockchain.json`: La cadena de bloques con los datos de la simulación.
- `reporte.txt`: Reporte final con la validación y estadísticas.