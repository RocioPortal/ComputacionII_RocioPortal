import argparse

# 1️ Crear un objeto ArgumentParser
parser = argparse.ArgumentParser(description="Ejemplo de argparse")

# 2 Agregar argumentos
parser.add_argument("nombre", help="Nombre de la persona")
parser.add_argument("-e", "--edad", type=int, help="Edad de la persona (opcional)")

# 3 Analizar argumentos
args = parser.parse_args()

# 4 Usar los valores de los argumentos
print(f"Hola, {args.nombre}!")
if args.edad:
    print(f"Tienes {args.edad} años.")
