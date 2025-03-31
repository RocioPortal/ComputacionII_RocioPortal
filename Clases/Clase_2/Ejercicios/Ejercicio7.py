import os, time

def crear_hijo(num):
    pid = os.fork()
    if pid == 0:
        print(f"Hijo {num}. PID: {os.getpid()}, PPID: {os.getppid()}")
        time.sleep(2)  
        print(f"Hijo {num} finaliza.")
        os._exit(0)
    return pid

def main():
    print(f"Proceso padre. PID: {os.getpid()}")

    # Crear tres hijos en paralelo
    hijos = [crear_hijo(i) for i in range(1, 4)]

    for pid in hijos:
        os.waitpid(pid, 0)

    print("Padre finaliza.")

if __name__ == "__main__":
    main()
