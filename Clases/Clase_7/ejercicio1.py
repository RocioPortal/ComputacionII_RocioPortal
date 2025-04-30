import signal
import os
import time

def manejador_sigint(signum, frame):
    print(f"\nSeñal recibida: {signum} (SIGINT)")
    print("Interrumpiendo de forma controlada...")

# Asignar el manejador a SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, manejador_sigint)

print(f"Mi PID es: {os.getpid()}")
print("Esperando señales... presioná Ctrl+C para probar.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("KeyboardInterrupt: no debería llegar si SIGINT es manejada.")