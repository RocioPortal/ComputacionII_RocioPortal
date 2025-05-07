from multiprocessing import Process

def saludar():
    print("¡Hola desde otro proceso!")

if __name__ == '__main__':
    p = Process(target=saludar)
    p.start()
    p.join()
    print("¡Proceso finalizado!")