import os

def main():
    pid = os.fork()  #nuevo proceso

    if pid > 0:
        #proceso padre
        print(f"Soy el proceso padre. PID: {os.getpid()}, PPID: {os.getppid()}")
    else:
        #proceso hijo
        print(f"Soy el proceso hijo. PID: {os.getpid()}, PPID: {os.getppid()}")

if __name__ == "__main__":
    main()
