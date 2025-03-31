import os, time, random

def atender_cliente(cliente_id):
    pid = os.fork()
    if pid == 0:
        print(f"Atendiendo cliente {cliente_id}. PID: {os.getpid()}, PPID: {os.getppid()}")
        time.sleep(random.randint(2, 5)) 
        print(f"Cliente {cliente_id} atendido. PID: {os.getpid()}")
        os._exit(0)

def main():
    print(f"Servidor iniciado. PID: {os.getpid()}")

    clientes = 5  # Número de clientes a atender
    for i in range(1, clientes + 1):
        atender_cliente(i)
        time.sleep(1) 

    for _ in range(clientes):
        os.wait()

    print("Servidor finaliza.")

if __name__ == "__main__":
    main()
