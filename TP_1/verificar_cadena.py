import json
import hashlib
import numpy as np

def calcular_hash(prev_hash, timestamp, datos):
    """
    Función para calcular el hash. Tiene que ser la misma que en el otro script.
    """
    block_string = str(prev_hash) + str(timestamp) + json.dumps(datos, sort_keys=True)
    return hashlib.sha256(block_string.encode()).hexdigest()

def verificar_y_reportar():
    """
    Función principal que lee el json, lo revisa y crea el reporte.
    """
    print("Iniciando la verificación de la cadena...")
    
    try:
        with open("blockchain.json", "r") as f:
            cadena = json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró 'blockchain.json'.")
        print("Asegúrate de haber ejecutado 'sistema_biometrico.py' primero.")
        return
    except json.JSONDecodeError:
        print("Error: El archivo 'blockchain.json' parece estar corrupto.")
        return

    # Verifico la integridad de la cadena
    prev_hash = "0" * 64
    errores = 0
    
    for i, bloque in enumerate(cadena):
        # Reviso que el hash anterior coincida
        if bloque["prev_hash"] != prev_hash:
            print(f"Error de encadenamiento en el bloque {i}:")
            print(f"   - Hash previo esperado: {prev_hash}")
            print(f"   - Hash previo guardado: {bloque['prev_hash']}")
            errores += 1
            # Si un hash no coincide, corto el bucle porque ya no tiene sentido seguir
            break 

        # Vuelvo a calcular el hash del bloque para ver si los datos fueron alterados
        hash_recalculado = calcular_hash(
            bloque["prev_hash"],
            bloque["timestamp"],
            bloque["datos"]
        )
        if bloque["hash"] != hash_recalculado:
            print(f"Corrupción de datos en el bloque {i}:")
            print(f"   - Hash guardado:    {bloque['hash']}")
            print(f"   - Hash recalculado: {hash_recalculado}")
            errores += 1

        # Actualizo el hash para la siguiente iteración
        prev_hash = bloque["hash"]

    if errores == 0:
        print("Verificación completada. La cadena es íntegra.")
    else:
        print(f"Verificación fallida. Se encontraron {errores} errores en la cadena.")
        # No genero el reporte si la cadena está corrupta
        return 

    # Ahora genero el reporte si todo salió bien
    if not cadena:
        print("La cadena está vacía, no se puede generar un reporte.")
        return

    total_bloques = len(cadena)
    bloques_con_alerta = sum(1 for bloque in cadena if bloque["alerta"])
    
    # Junto todos los datos para sacar los promedios
    frecuencias = [b["datos"]["frecuencia"]["media"] for b in cadena]
    presiones_sist = [b["datos"]["presion"]["media"][0] for b in cadena]
    presiones_diast = [b["datos"]["presion"]["media"][1] for b in cadena]
    oxigenos = [b["datos"]["oxigeno"]["media"] for b in cadena]
    
    # Calculo los promedios
    prom_frecuencia = np.mean(frecuencias) if frecuencias else 0
    prom_presion_sist = np.mean(presiones_sist) if presiones_sist else 0
    prom_presion_diast = np.mean(presiones_diast) if presiones_diast else 0
    prom_oxigeno = np.mean(oxigenos) if oxigenos else 0

    # Armo el string del reporte
    reporte_str = f"""
========================================
REPORTE FINAL DE ANÁLISIS BIOMÉTRICO
========================================

1. Resumen de la Cadena
-------------------------------------
Total de bloques: {total_bloques}
Bloques con alertas: {bloques_con_alerta}
Integridad de la cadena: Verificada

2. Promedios Generales
-------------------------------------
- Frecuencia Cardíaca: {prom_frecuencia:.2f} lpm
- Presión Arterial:    {prom_presion_sist:.2f} / {prom_presion_diast:.2f} mmHg (Sist/Diast)
- Saturación de Oxígeno: {prom_oxigeno:.2f} %

========================================
"""
    
    # Guardo el reporte en reporte.txt
    try:
        with open("reporte.txt", "w") as f:
            f.write(reporte_str.strip())
        print("Reporte 'reporte.txt' generado con éxito.")
    except IOError as e:
        print(f"Error al intentar escribir el archivo de reporte: {e}")

if __name__ == "__main__":
    verificar_y_reportar()