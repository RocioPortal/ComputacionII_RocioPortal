import os

def main():
    pid = os.fork()

    if pid == 0:
        print(f"Hijo ejecutando 'ls -l'. PID: {os.getpid()}, PPID: {os.getppid()}")
        os.execlp("ls", "ls", "-l")
        print("Error: exec() falló")
        os._exit(1)

    else:
        os.waitpid(pid, 0)
        print(f"Padre finaliza. PID: {os.getpid()}")

if __name__ == "__main__":
    main()
