import multiprocessing
import time
import datetime
import random
import json
import hashlib
import numpy as np
import os
from collections import deque

# --- Función de Hash ---

def calcular_hash(prev_hash, timestamp, datos):
    """Calcula el hash para un bloque. Tiene que ser igual en todos lados."""
    block_string = str(prev_hash) + str(timestamp) + json.dumps(datos, sort_keys=True)
    return hashlib.sha256(block_string.encode()).hexdigest()

# --- Procesos Hijos ---

def proceso_analizador(nombre_metrica, pipe_conn, queue_verificador):
    """
    Este proceso analiza una métrica. Recibe datos, calcula stats
    en una ventana de 30 seg y manda el resultado al verificador.
    """
    ventana_datos = deque(maxlen=30)
    print(f"[Analizador {nombre_metrica.upper()}] Iniciado (PID: {os.getpid()})")

    while True:
        try:
            # Espero a que lleguen datos del proceso principal
            dato_completo = pipe_conn.recv()
            if dato_completo is None:  # Si llega None, es la señal para terminar
                break

            # Saco la métrica que le toca a este proceso
            valor_metrica = dato_completo[nombre_metrica]
            
            ventana_datos.append(valor_metrica)

            # Calculo las estadísticas
            if nombre_metrica == "presion":
                # Para la presión, numpy saca media y desvío por columna (sist/diast)
                media = np.mean(ventana_datos, axis=0).tolist()
                desv = np.std(ventana_datos, axis=0).tolist()
            else:
                media = np.mean(ventana_datos)
                desv = np.std(ventana_datos)
            
            # Armo el resultado y lo mando a la cola del verificador
            resultado = {
                "tipo": nombre_metrica,
                "timestamp": dato_completo["timestamp"],
                "media": media,
                "desv": desv
            }
            queue_verificador.put(resultado)

        except EOFError:
            # Pasa si el pipe se cierra de repente
            break

    print(f"[Analizador {nombre_metrica.upper()}] Finalizando.")
    pipe_conn.close()


def proceso_verificador(queue_verificador):
    """
    Recibe los resultados de los 3 analizadores, arma los bloques
    y los va guardando en el archivo blockchain.json.
    """
    print(f"[Verificador] Iniciado (PID: {os.getpid()})")
    blockchain = []
    prev_hash = "0" * 64  # Hash para el bloque génesis
    buffer_resultados = {} # Buffer por si los resultados llegan desordenados

    # Intento cargar la blockchain si ya existe
    if os.path.exists("blockchain.json"):
        try:
            with open("blockchain.json", "r") as f:
                blockchain = json.load(f)
                if blockchain:
                    prev_hash = blockchain[-1]['hash']
            print("[Verificador] Se cargó una blockchain existente.")
        except (json.JSONDecodeError, IndexError):
            print("[Verificador] El archivo blockchain.json está mal o vacío. Empiezo de cero.")

    # Bucle principal, va a procesar 60 bloques
    for i in range(60):
        # Espero los 3 resultados para el mismo timestamp
        resultados_actuales = {}
        while len(resultados_actuales) < 3:
            res = queue_verificador.get()
            timestamp = res["timestamp"]
            
            if timestamp not in buffer_resultados:
                buffer_resultados[timestamp] = {}
            
            buffer_resultados[timestamp][res["tipo"]] = {
                "media": res["media"], "desv": res["desv"]
            }
            
            # Si ya tengo los 3, los proceso
            if len(buffer_resultados[timestamp]) == 3:
                resultados_actuales = buffer_resultados.pop(timestamp)
                break
        
        # Reviso si hay que marcar una alerta
        alerta = False
        media_frec = resultados_actuales["frecuencia"]["media"]
        media_oxigeno = resultados_actuales["oxigeno"]["media"]
        media_presion_sistolica = resultados_actuales["presion"]["media"][0]

        if not (media_frec < 200):
            alerta = True
        if not (90 <= media_oxigeno <= 100):
            alerta = True
        if not (media_presion_sistolica < 200):
            alerta = True

        # Armo el bloque nuevo
        nuevo_bloque = {
            "index": len(blockchain),
            "timestamp": timestamp,
            "datos": resultados_actuales,
            "alerta": alerta,
            "prev_hash": prev_hash
        }
        
        hash_actual = calcular_hash(
            prev_hash,
            timestamp,
            nuevo_bloque["datos"]
        )
        nuevo_bloque["hash"] = hash_actual
        
        # Lo agrego a la cadena y guardo en el archivo
        blockchain.append(nuevo_bloque)
        with open("blockchain.json", "w") as f:
            json.dump(blockchain, f, indent=4)
            
        print(
            f"[Verificador] Bloque {nuevo_bloque['index']} añadido. "
            f"Hash: {hash_actual[:10]}... | Alerta: {alerta}"
        )
        
        # Guardo el hash para el próximo bloque
        prev_hash = hash_actual
        
    print("[Verificador] Finalizando.")

# --- Proceso Principal ---

if __name__ == "__main__":
    print("--- Iniciando Sistema de Análisis Biométrico ---")
    
    # Preparo los pipes y la cola para comunicar los procesos
    queue_verificador = multiprocessing.Queue()
    
    parent_conn_a, child_conn_a = multiprocessing.Pipe()
    parent_conn_b, child_conn_b = multiprocessing.Pipe()
    parent_conn_c, child_conn_c = multiprocessing.Pipe()

    pipes_info = {
        "frecuencia": (parent_conn_a, child_conn_a),
        "presion": (parent_conn_b, child_conn_b),
        "oxigeno": (parent_conn_c, child_conn_c),
    }

    # Creo los procesos hijos
    procesos = []
    for metrica, (_, child_conn) in pipes_info.items():
        p = multiprocessing.Process(
            target=proceso_analizador, 
            args=(metrica, child_conn, queue_verificador)
        )
        procesos.append(p)
    
    p_verificador = multiprocessing.Process(
        target=proceso_verificador, 
        args=(queue_verificador,)
    )
    procesos.append(p_verificador)

    # Inicio todos los procesos
    for p in procesos:
        p.start()
        
    # El padre ya no necesita los pipes de los hijos, los cierro de este lado
    for _, child_conn in pipes_info.values():
        child_conn.close()

    # Bucle principal para generar y enviar datos durante 60 segundos
    for i in range(60):
        # Genero un dato biométrico (con rangos para que salten alertas)
        datos_biometricos = {
            "timestamp": datetime.datetime.now().isoformat(),
            "frecuencia": random.randint(60, 220),
            "presion": [random.randint(110, 225), random.randint(70, 110)], 
            "oxigeno": random.randint(85, 100)
        }
        
        print(f"[Principal] T={i+1:02d}/60 -> Enviando: Freq={datos_biometricos['frecuencia']}, Pres={datos_biometricos['presion']}, Oxi={datos_biometricos['oxigeno']}%")

        # Mando el mismo dato a los 3 analizadores
        for parent_conn, _ in pipes_info.values():
            parent_conn.send(datos_biometricos)
        
        time.sleep(1)

    # Terminó la simulación, mando la señal de stop (None)
    print("[Principal] Finalizando. Avisando a los procesos hijos...")
    for parent_conn, _ in pipes_info.values():
        parent_conn.send(None) 
        parent_conn.close()

    # Espero a que todos los procesos terminen bien
    for p in procesos:
        p.join()

    print("--- Sistema finalizado. ---")
