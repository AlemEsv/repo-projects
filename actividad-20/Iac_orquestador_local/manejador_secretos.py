import os
import json


RUTA_PERSONALIZADA_SECRETOS = r"C:\Users\windows10\Desktop\actividad20\secreto.json"

IDENTIFICADOR_APP_EN_JSON = "mi_aplicacion_terraform"  

SUB_CLAVE_API_KEY = "api_key" 


def obtener_api_key_desde_path_personalizado():
    """
    Lee la API key del archivo de secretos ubicado en RUTA_PERSONALIZADA_SECRETOS.
    Retorna la API key como string, o None si no se puede obtener.
    """
    print(f"Intentando leer secretos desde: {RUTA_PERSONALIZADA_SECRETOS}")

    if not os.path.exists(RUTA_PERSONALIZADA_SECRETOS):
        print(f"Error: Archivo de secretos no encontrado en '{RUTA_PERSONALIZADA_SECRETOS}'.")
        print("Por favor, verifica la RUTA_PERSONALIZADA_SECRETOS en el script y que el archivo exista.")
        return None

    try:
        with open(RUTA_PERSONALIZADA_SECRETOS, 'r') as f:
            secrets_data = json.load(f)
        
        app_specific_secrets = secrets_data.get(IDENTIFICADOR_APP_EN_JSON)
        if not app_specific_secrets:
            print(f"Error: El identificador '{IDENTIFICADOR_APP_EN_JSON}' no fue encontrado "
                  f"en el archivo '{RUTA_PERSONALIZADA_SECRETOS}'.")
            return None

        api_key = app_specific_secrets.get(SUB_CLAVE_API_KEY)
        if not api_key:
            print(f"Error: La sub-clave '{SUB_CLAVE_API_KEY}' no fue encontrada bajo el identificador "
                  f"'{IDENTIFICADOR_APP_EN_JSON}' en el archivo '{RUTA_PERSONALIZADA_SECRETOS}'.")
            return None
            
        return api_key

    except json.JSONDecodeError:
        print(f"Error: El archivo de secretos '{RUTA_PERSONALIZADA_SECRETOS}' no contiene un JSON válido.")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer el archivo de secretos: {e}")
        return None

def ejemplo_demostracion_uso_key():
    """Función de ejemplo que obtiene y (de forma segura) indica que usaría la API key."""
    print("\n--- Ejemplo de uso de la API key ---")
    api_key_leida = obtener_api_key_desde_path_personalizado()

    if api_key_leida:
        print(f"API Key obtenida exitosamente desde la ruta personalizada.")
        num_chars_a_mostrar = min(4, len(api_key_leida)) 
        print(f"Verificación (primeros {num_chars_a_mostrar} caracteres): {api_key_leida[:num_chars_a_mostrar]}{'*' * (len(api_key_leida) - num_chars_a_mostrar)}")
        
        print("\nEn un flujo de trabajo real, esta API key se podría:")
        print("1. Pasar como variable de entorno a un proceso de Terraform:")
        print(f'   Ej: os.environ["TF_VAR_nombre_variable_api_key"] = "{api_key_leida[:2]}...{api_key_leida[-2:]}"')
        print("2. Usar para configurar un cliente de API directamente en Python.")
        print("3. Escribir en un archivo .tfvars (que debe estar en .gitignore).")
    else:
        print("No se pudo obtener la API key. No se puede proceder con la operación que la requiere.")

if __name__ == "__main__":
    ejemplo_demostracion_uso_key()