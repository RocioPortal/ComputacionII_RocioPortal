import os, time

def main():
    pid = os.fork()

    if pid == 0:
        print(f"Hijo (PID: {os.getpid()}) finaliza inmediatamente.")
        os._exit(0)  # El hijo termina

    else:
        print(f"Padre (PID: {os.getpid()}) deja al hijo en estado zombi...")
        time.sleep(5)  
        os.waitpid(pid, 0) 
        print("Padre recogió al hijo, ya no es zombi.")

if __name__ == "__main__":
    main()
