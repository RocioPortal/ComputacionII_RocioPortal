import os

def detectar_zombis():
    for pid in os.listdir("/proc"):
        if pid.isdigit(): 
            try:
                with open(f"/proc/{pid}/status", "r") as f:
                    lines = f.readlines()

                estado = [line for line in lines if line.startswith("State:")][0]
                if "Z" in estado:  
                    ppid = [line for line in lines if line.startswith("PPid:")][0].split()[1]
                    nombre = [line for line in lines if line.startswith("Name:")][0].split()[1]
                    
                    print(f"Zombi encontrado: PID={pid}, PPID={ppid}, Nombre={nombre}")
            except FileNotFoundError:
                continue  

def main():
    print("Buscando procesos zombis en el sistema...")
    detectar_zombis()

if __name__ == "__main__":
    main()
