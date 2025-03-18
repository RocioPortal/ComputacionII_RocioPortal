import argparse

# Crear el analizador
parser = argparse.ArgumentParser(description="Ejemplo avanzado de argparse")

# Argumento obligatorio (posición)
parser.add_argument("nombre", help="Nombre de la persona")

# Argumento opcional con valor predeterminado
parser.add_argument("-e", "--edad", type=int, default=18, help="Edad de la persona (opcional, por defecto 18)")

# Argumento booleano (activado si se usa la opción)
parser.add_argument("-v", "--verbose", action="store_true", help="Activa el modo detallado")

# Procesar los argumentos
args = parser.parse_args()

# Mostrar resultados
print(f"Hola, {args.nombre}!")
print(f"Tienes {args.edad} años.")

if args.verbose:
    print("Modo detallado activado.")
