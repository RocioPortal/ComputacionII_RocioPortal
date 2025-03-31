import os

def main():
    # Primer fork: primer hijo
    pid1 = os.fork()

    if pid1 == 0:
        #primer hijo
        print(f"Primer hijo. PID: {os.getpid()}, PPID: {os.getppid()}")
        os._exit(0)  # Termina el hijo

    # Segundo fork: segundo hijo (se ejecuta solo en el padre)
    pid2 = os.fork()

    if pid2 == 0:
        # Código del segundo hijo
        print(f"Segundo hijo. PID: {os.getpid()}, PPID: {os.getppid()}")
        os._exit(0)  # Termina el hijo

    # Código del padre (espera a ambos hijos)
    os.waitpid(pid1, 0)
    os.waitpid(pid2, 0)
    print(f"Padre finaliza. PID: {os.getpid()}")

if __name__ == "__main__":
    main()
