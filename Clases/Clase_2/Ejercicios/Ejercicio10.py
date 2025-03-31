import os
import time
import random

def proceso_huerfano():
    pid = os.fork()

    if pid == 0:
        time.sleep(3) 
        print(f"Proceso huérfano. PID: {os.getpid()}, PPID: {os.getppid()}")
        
        print("Ejecutando comando en el proceso huérfano...")
        os.system("whoami") 
        
        os._exit(0)
    
    else:
        print(f"Padre. PID: {os.getpid()} finaliza antes que el hijo.")
        os._exit(0) 

def main():
    print(f"Iniciando el proceso huérfano. PID: {os.getpid()}")
    proceso_huerfano()

if __name__ == "__main__":
    main()
