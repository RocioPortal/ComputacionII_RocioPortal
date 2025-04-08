import os
import time

FILENAME = "comunicacion.txt"

def proceso_hijo():
    with open(FILENAME, "a") as f:
        for i in range(5):
            f.write(f"Hijo escribe línea {i}\n")
            time.sleep(0.1)

def proceso_padre():
    with open(FILENAME, "a") as f:
        for i in range(5):
            f.write(f"Padre escribe línea {i}\n")
            time.sleep(0.1)

def leer_archivo():
    print("\nContenido final del archivo:")
    with open(FILENAME, "r") as f:
        print(f.read())

if __name__ == "__main__":
    # Asegurarse de que el archivo esté vacío al comienzo
    open(FILENAME, "w").close()

    pid = os.fork()

    if pid == 0:
        # Proceso hijo
        proceso_hijo()
        os._exit(0)
    else:
        # Proceso padre
        proceso_padre()
        os.wait()  # Espera a que el hijo termine
        leer_archivo()
