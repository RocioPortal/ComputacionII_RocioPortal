from multiprocessing import Process, Queue, Lock, current_process
import time
import random

def tarea_concurrente(numero, queue, lock):
    tiempo = random.uniform(0.5, 1.5)
    with lock:
        print(f"[{current_process().name}] Procesando número {numero} (duración estimada: {tiempo:.2f}s)")
    time.sleep(tiempo)
    resultado = numero * numero
    queue.put((numero, resultado))
    with lock:
        print(f"[{current_process().name}] Resultado listo: {numero}^2 = {resultado}")

if __name__ == '__main__':
    numeros = [1, 2, 3, 4, 5]
    procesos = []
    queue = Queue()
    lock = Lock()

    # Crear y lanzar los procesos
    for n in numeros:
        p = Process(target=tarea_concurrente, args=(n, queue, lock))
        procesos.append(p)
        p.start()

    # Esperar a que todos los procesos terminen
    for p in procesos:
        p.join()

    # Recoger los resultados
    print("\nResultados finales:")
    while not queue.empty():
        numero, resultado = queue.get()
        print(f"{numero}^2 = {resultado}")