import os

# Puedes ampliar esta lista según tu necesidad
EXTENSIONES_PERMITIDAS = {
    ".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".h", ".json", ".xml", ".sh", ".yaml", ".yml","tf", "tfvars", "tfvars.json"
}

CARPETAS_IGNORADAS = {".git", "__pycache__", "node_modules", ".vscode", "venv", ".idea", ".env"}

def extraer_codigo(directorio_raiz, archivo_salida=None):
    contenido_total = []

    for ruta_actual, carpetas, archivos in os.walk(directorio_raiz):
        # Elimina carpetas ignoradas del recorrido
        carpetas[:] = [c for c in carpetas if c not in CARPETAS_IGNORADAS]

        for archivo in archivos:
            ruta_archivo = os.path.join(ruta_actual, archivo)
            _, extension = os.path.splitext(archivo)

            if extension.lower() in EXTENSIONES_PERMITIDAS:
                try:
                    with open(ruta_archivo, "r", encoding="utf-8") as f:
                        codigo = f.read()
                    encabezado = f"\n--- Archivo: {ruta_archivo} ---\n"
                    contenido_total.append(encabezado + codigo)
                except Exception as e:
                    print(f"[Error] No se pudo leer: {ruta_archivo} ({e})")

    codigo_final = "\n".join(contenido_total)

    if archivo_salida:
        try:
            with open(archivo_salida, "w", encoding="utf-8") as f_out:
                f_out.write(codigo_final)
            print(f"\n✅ Código extraído y guardado en '{archivo_salida}'")
        except Exception as e:
            print(f"[Error] No se pudo escribir el archivo de salida: {e}")
    else:
        print(codigo_final)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extrae el código fuente de un proyecto en una sola salida.")
    parser.add_argument(
        "directorio",
        nargs="?",
        default=".",
        help="Ruta al directorio del proyecto (por defecto: directorio actual)."
    )
    parser.add_argument(
        "-o", "--output",
        help="Ruta del archivo donde guardar el código extraído (opcional)."
    )

    args = parser.parse_args()
    extraer_codigo(args.directorio, args.output)