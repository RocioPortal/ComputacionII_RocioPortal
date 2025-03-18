import sys
import getopt

def main():
    # Definir opciones cortas (-n) y largas (--name)
    opciones_cortas = "n:"
    opciones_largas = ["name="]

    try:
        # Obtener argumentos con getopt
        opts, args = getopt.getopt(sys.argv[1:], opciones_cortas, opciones_largas)
    except getopt.GetoptError as err:
        print(f"Error: {err}")
        sys.exit(1)

    nombre = "Desconocido"  # Valor por defecto
    for opt, arg in opts:
        if opt in ("-n", "--name"):
            nombre = arg

    print(f"¡Hola, {nombre}!")

if __name__ == "__main__":
    main()
