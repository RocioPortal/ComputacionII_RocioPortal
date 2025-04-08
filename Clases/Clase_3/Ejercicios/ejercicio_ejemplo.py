import os
import time

def child_process_1():
    print(f"Hijo 1 (PID: {os.getpid()}), esperando 3 segundos...")
    time.sleep(3)
    print(f"Hijo 1 (PID: {os.getpid()}) terminó su tarea")

def child_process_2():
    print(f"Hijo 2 (PID: {os.getpid()}), esperando 2 segundos...")
    time.sleep(2)
    print(f"Hijo 2 (PID: {os.getpid()}) terminó su tarea")

def main():
    print(f"Proceso padre (PID: {os.getpid()}) iniciando")
    
    pid1 = os.fork()
    if pid1 == 0:
        child_process_1()
        os._exit(0)
    
    pid2 = os.fork()
    if pid2 == 0:
        child_process_2()
        os._exit(0)
    
    os.waitpid(pid1, 0)
    os.waitpid(pid2, 0)
    
    print(f"Proceso padre (PID: {os.getpid()}) finalizando")

if __name__ == "__main__":
    main()