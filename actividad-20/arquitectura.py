import os
import argparse

# Caracteres para dibujar el árbol (puedes personalizarlos)
PREFIX_BRANCH = "├── "  # Rama intermedia
PREFIX_LAST_BRANCH = "└── "  # Última rama
PREFIX_PARENT_PIPE = "│   "  # Tubería para niveles superiores (cuando hay más hermanos)
PREFIX_PARENT_SPACE = "    "  # Espacio para niveles superiores (cuando es el último hermano)

def generate_tree(directory_path, prefix="", level=-1, max_depth=None, ignore_list=None, show_hidden=False, files_only=False, dirs_only=False):
    """
    Genera y muestra la estructura de árbol de un directorio.

    Args:
        directory_path (str): La ruta al directorio raíz del proyecto.
        prefix (str): El prefijo de la línea actual (para la indentación y las líneas del árbol).
        level (int): Nivel actual de profundidad (usado para max_depth).
        max_depth (int, optional): Profundidad máxima a mostrar. None para ilimitada.
        ignore_list (list, optional): Lista de nombres de archivos/directorios a ignorar.
        show_hidden (bool): Si es True, muestra archivos/directorios ocultos (que empiezan con .).
        files_only (bool): Si es True, solo muestra archivos.
        dirs_only (bool): Si es True, solo muestra directorios.
    """
    if ignore_list is None:
        ignore_list = []

    if max_depth is not None and level >= max_depth:
        return

    try:
        # Obtener todos los elementos, excluyendo los ignorados y ocultos si es necesario
        entries = []
        for entry_name in os.listdir(directory_path):
            if entry_name in ignore_list:
                continue
            if not show_hidden and entry_name.startswith('.'):
                continue
            
            full_path = os.path.join(directory_path, entry_name)
            is_dir = os.path.isdir(full_path)

            if files_only and is_dir:
                continue
            if dirs_only and not is_dir:
                continue
                
            entries.append((entry_name, is_dir, full_path))

        # Ordenar: directorios primero, luego archivos, ambos alfabéticamente
        entries.sort(key=lambda x: (not x[1], x[0].lower()))

    except PermissionError:
        print(f"{prefix}{PREFIX_BRANCH}[Error: Permiso denegado] {os.path.basename(directory_path)}")
        return
    except FileNotFoundError:
        # Esto no debería ocurrir si se llama desde un directorio válido, pero es buena práctica
        print(f"Error: Directorio '{directory_path}' no encontrado.")
        return

    pointers = [PREFIX_BRANCH] * (len(entries) - 1) + [PREFIX_LAST_BRANCH]

    for i, (name, is_dir, full_path) in enumerate(entries):
        pointer = pointers[i]
        print(f"{prefix}{pointer}{name}")

        if is_dir:
            # Determinar el prefijo para la siguiente llamada recursiva
            extension = PREFIX_PARENT_PIPE if i < len(entries) - 1 else PREFIX_PARENT_SPACE
            generate_tree(
                full_path,
                prefix + extension,
                level + 1,
                max_depth,
                ignore_list,
                show_hidden,
                files_only,
                dirs_only
            )

def main():
    parser = argparse.ArgumentParser(description="Genera un árbol de la estructura de directorios de un proyecto.")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Ruta al directorio del proyecto (por defecto: directorio actual)."
    )
    parser.add_argument(
        "-d", "--max-depth",
        type=int,
        help="Profundidad máxima del árbol a mostrar."
    )
    parser.add_argument(
        "-i", "--ignore",
        nargs="+",
        default=[".git", "__pycache__", ".vscode", ".idea", "node_modules", "venv", ".env"], # Algunos comunes
        help="Lista de nombres de archivos/directorios a ignorar (separados por espacio)."
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Mostrar archivos y directorios ocultos (que empiezan con '.')."
    )
    parser.add_argument(
        "--files-only",
        action="store_true",
        help="Mostrar solo archivos en el árbol."
    )
    parser.add_argument(
        "--dirs-only",
        action="store_true",
        help="Mostrar solo directorios en el árbol."
    )

    args = parser.parse_args()

    if args.files_only and args.dirs_only:
        print("Error: No se pueden usar --files-only y --dirs-only al mismo tiempo.")
        return

    # Normalizar la ruta y obtener el nombre base para la raíz del árbol
    root_directory = os.path.abspath(args.path)

    if not os.path.isdir(root_directory):
        print(f"Error: La ruta especificada '{args.path}' no es un directorio válido.")
        return

    print(f"{os.path.basename(root_directory)}/") # Imprime la raíz del árbol
    generate_tree(
        root_directory,
        level=0, # Empezamos en el nivel 0 para los hijos directos de la raíz
        max_depth=args.max_depth,
        ignore_list=args.ignore,
        show_hidden=args.all,
        files_only=args.files_only,
        dirs_only=args.dirs_only
    )

if __name__ == "__main__":
    main()