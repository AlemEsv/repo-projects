import os

EXTENSIONES_PERMITIDAS = {".py", ".json", ".tf", ".md", ".txt"}
CARPETAS_IGNORADAS = {".git", "__pycache__", "node_modules", ".vscode", "venv", ".idea", ".env"}

def extraer_y_guardar(directorio_raiz=".", archivo_salida="codigo_extraido.txt"):
    contenido_total = []

    for ruta_actual, carpetas, archivos in os.walk(directorio_raiz):
        # Ignorar carpetas no deseadas
        carpetas[:] = [c for c in carpetas if c not in CARPETAS_IGNORADAS]

        for archivo in archivos:
            ruta_archivo = os.path.join(ruta_actual, archivo)
            _, extension = os.path.splitext(archivo)

            if extension.lower() in EXTENSIONES_PERMITIDAS:
                try:
                    with open(ruta_archivo, "r", encoding="utf-8") as f:
                        codigo = f.read()
                    encabezado = f"\n\n--- Archivo: {ruta_archivo} ---\n"
                    contenido_total.append(encabezado + codigo)
                except Exception as e:
                    print(f"[Error] No se pudo leer: {ruta_archivo} ({e})")

    try:
        with open(archivo_salida, "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(contenido_total))
        print(f"\n✅ Código extraído y guardado en '{archivo_salida}'")
    except Exception as e:
        print(f"[Error] No se pudo escribir el archivo de salida: {e}")

if __name__ == "__main__":
    extraer_y_guardar()