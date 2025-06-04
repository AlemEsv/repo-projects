#!/usr/bin/env python3

import time
import os
import subprocess
import click
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent

# Directorio del script actual para construir rutas relativas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR_TO_WATCH = os.path.join(SCRIPT_DIR, "modules", "simulated_app")
ENVIRONMENTS_BASE_DIR = os.path.join(SCRIPT_DIR, "environments")
GENERATE_ENVS_SCRIPT = os.path.join(SCRIPT_DIR, "generate_envs.py")

# Estado para evitar ejecuciones múltiples muy seguidas
last_triggered_time = 0
COOLDOWN_PERIOD = 5 # segundos

def get_existing_env_configs():
    """
    Intenta deducir la configuración (prefijo, número) de los entornos existentes.
    Esto es una heurística y puede necesitar ajustes según tu nomenclatura.
    Asume que los directorios en environments/ siguen un patrón como 'prefixN'.
    Devuelve una lista de tuplas (prefix, count, full_path).
    """
    configs = []
    if not os.path.isdir(ENVIRONMENTS_BASE_DIR):
        click.secho(f"Warning: Environments base directory '{ENVIRONMENTS_BASE_DIR}' not found.", fg="yellow")
        return configs

    for item_name in os.listdir(ENVIRONMENTS_BASE_DIR):
        item_path = os.path.join(ENVIRONMENTS_BASE_DIR, item_name)
        if os.path.isdir(item_path):
            # Intenta extraer prefijo y número. Ejemplo: 'staging12' -> ('staging', 12)
            # Esto es simplista. Una mejor manera sería almacenar metadatos al crear.
            prefix_parts = []
            num_str = ""
            for char in reversed(item_name):
                if char.isdigit():
                    num_str = char + num_str
                else:
                    prefix_parts.insert(0, char)
            
            prefix = "".join(prefix_parts)
            if num_str and prefix:
                try:
                    # Asumimos que si hay un número al final, es parte de una secuencia única por prefijo.
                    # Para simplificar, regeneraremos cada "grupo" de prefijo con su máximo contador.
                    # O, más simple: regeneramos cada directorio individualmente.
                    # Por ahora, solo capturamos el nombre para regenerar ese entorno específico.
                    # Esta función podría ser más inteligente para agrupar.
                    # Para este ejemplo, vamos a regenerar CADA entorno individualmente
                    # pasándole su nombre completo como prefijo y count=1.
                    configs.append({"prefix": item_name, "count": 1, "out_dir_leaf": item_name})
                except ValueError:
                    click.secho(f"Could not parse number from environment: {item_name}", fg="yellow")
            elif item_name: # Si no hay número, trátalo como un prefijo único
                 configs.append({"prefix": item_name, "count": 1, "out_dir_leaf": item_name})


    # Para evitar duplicados si varios items comparten el mismo prefijo base y solo cambia el número final
    # Por ejemplo, si tenemos app1, app2, app_drift_demo
    # El enfoque anterior nos daría:
    # [{'prefix': 'app1', 'count': 1, 'out_dir_leaf': 'app1'},
    #  {'prefix': 'app2', 'count': 1, 'out_dir_leaf': 'app2'},
    #  {'prefix': 'app_drift_demo', 'count': 1, 'out_dir_leaf': 'app_drift_demo'}]
    # Esto es lo que queremos para regenerar cada uno individualmente.
    return configs


def regenerate_environments():
    """
    Llama al script generate_envs.py para todos los entornos detectados.
    """
    global last_triggered_time
    current_time = time.time()
    if current_time - last_triggered_time < COOLDOWN_PERIOD:
        click.echo("Cooldown active, skipping regeneration.")
        return
    last_triggered_time = current_time

    click.secho("Detected changes in module. Regenerating environments...", fg="cyan", bold=True)
    
    env_configs = get_existing_env_configs()
    if not env_configs:
        click.secho("No existing environment configurations found to regenerate.", fg="yellow")
        return

    all_successful = True
    for config in env_configs:
        # Para regenerar un entorno específico, pasamos su nombre como prefijo y count=1
        # y ajustamos out_dir para que apunte directamente al subdirectorio.
        # Esto es un HACK porque generate_envs.py espera crear N entornos BAJO out_dir.
        # Sería mejor si generate_envs.py tuviera una opción para actualizar un solo entorno.
        #
        # Alternativa: generate_envs.py podría tener una opción --update-all-in <dir>
        #
        # Por ahora, la forma más simple es llamar a generate_envs.py por cada
        # "grupo" detectado. Si `app1`, `app2` son un grupo, y `staging1` es otro.
        # Si `generate_envs.py` crea `prefix1`, `prefix2`...`prefixN`, necesitamos saber `N` y `prefix`.
        # La función `get_existing_env_configs` es muy básica.
        #
        # Supongamos que `generate_envs.py` puede tomar un `--target-env-name`
        # o que podemos reconstruir los parámetros originales.
        #
        # Por simplicidad aquí, asumiremos que cada directorio en `environments/`
        # fue creado con `generate_envs.py --prefix <dirname> --count 1`.
        # Esto NO es ideal si tenías `generate_envs.py --prefix app --count 10`.
        #
        # *Mejor Enfoque para Regeneración*:
        # El script `generate_envs.py` debería tener un modo "update".
        # Por ahora, vamos a re-ejecutar con `--force` para cada entorno individual.
        # Esto significa que `get_existing_env_configs` debe dar el nombre del directorio.

        env_name = config['out_dir_leaf'] # ej: "staging1", "app_drift_demo"
        click.echo(f"\nRegenerating environment: {env_name}")
        
        # Llamamos a generate_envs.py para "crear" este entorno específico.
        # Usamos el nombre del entorno como prefijo y count=1.
        # IMPORTANTE: Esto sobrescribirá el directorio del entorno.
        # Necesitamos que generate_envs.py maneje esto correctamente (con --force).
        cmd = [
            "python", 
            GENERATE_ENVS_SCRIPT,
            "--prefix", env_name, # Usamos el nombre del dir como prefijo
            "--count", "1",       # Solo creamos/actualizamos este
            "--out-dir", ENVIRONMENTS_BASE_DIR, # El directorio base
            "--force"             # Para sobrescribir sin preguntar
        ]
        # Si `generate_envs.py` crea `<out_dir>/<prefix><count>`, entonces
        # si `prefix=staging1` y `count=1`, creará `environments/staging11`. ¡NO ES LO QUE QUEREMOS!
        #
        # Necesitamos que `generate_envs.py` pueda actualizar un directorio existente,
        # o que podamos pasarle el nombre exacto del directorio a operar.
        #
        # REVISIÓN DE LA LÓGICA DE `generate_envs.py`:
        # `generate_envs.py` crea `os.path.join(out_dir_abs, app_name)` donde `app_name = f"{prefix}{i}"`
        # Si queremos regenerar `environments/staging1`:
        #   Necesitamos llamar con un `prefix` y `count` que resulte en `app_name = "staging1"`.
        #   Si `prefix="staging1"` y `count=1`, entonces `app_name` será `staging11`.
        #
        # Solución más robusta:
        # 1. `generate_envs.py` podría tomar un argumento `--update <env_name>`
        # 2. O, almacenamos los parámetros originales de creación de cada entorno.
        #
        # Solución de compromiso para este ejemplo:
        # Asumimos que cada directorio en `environments` es un "prefijo" único que fue creado con count=1.
        # Entonces, si el dir es `staging1`, llamamos con `prefix=staging1`, `count=1`.
        # PERO `generate_envs.py` genera `staging11`.
        #
        # La forma más sencilla de *sobrescribir* un entorno existente llamado `staging1`
        # usando el `generate_envs.py` actual, sería modificar `generate_envs.py` para que
        # si el `app_name` (ej. `staging1`) ya existe, simplemente actualice sus archivos.
        # La opción `--force` ya hace que sobrescriba.
        # El problema es cómo hacer que `app_name` sea exactamente `staging1`.
        #
        # Si `prefix="staging"` y `count=1`, se crea `staging1`.
        # Si `prefix="app"` y `count=2`, se crean `app1`, `app2`.
        #
        # Necesitamos re-pensar `get_existing_env_configs`.
        # Debe agrupar por prefijo real y encontrar el N máximo.

        # NUEVO get_existing_env_configs (simplificado para el ejemplo)
        # Para este script, asumiremos que tenemos una lista de los PREFIJOS y COUNTS originales.
        # Como no la tenemos, haremos algo más simple:
        # Iteraremos sobre cada subdirectorio de `environments` y asumiremos que es un entorno
        # que fue creado con `prefix=<dirname>` y `count=1`. Esto NO es correcto
        # si fue creado con `prefix=app --count=10`.
        #
        # Por ahora, para que el watcher funcione, haremos una llamada genérica que podría no ser ideal
        # pero que al menos ejecutará `generate_envs.py`.
        #
        # El comando más seguro para "rehacer todo" si no conocemos los parámetros originales es
        # borrar y recrear, o que generate_envs.py tenga una lógica de "re-aplicar a todos".
        #
        # *** MEJOR SOLUCIÓN TEMPORAL: ***
        # Asumir que `generate_envs.py` se llamó con ciertos parámetros fijos para TODOS los entornos.
        # Esto es una simplificación fuerte.
        #
        # Por ejemplo, si todos tus entornos son `app1`...`app10`, llamarías:
        # python generate_envs.py --prefix app --count 10 --force
        #
        # Este script `watchdog` no puede saber mágicamente esos parámetros.
        #
        # Solución para este ejercicio:
        # Vamos a asumir que queremos regenerar CADA subdirectorio en `environments/`
        # como si fuera un entorno independiente.
        # `generate_envs.py` crea `<out_dir>/<prefix><count_num>`.
        # Si queremos regenerar `environments/staging1`, deberíamos llamar a `generate_envs.py`
        # de tal forma que el *resultado* sea `staging1`.
        # La forma más directa es que `generate_envs.py` acepte un nombre de entorno específico a (re)generar.
        #
        # Dado que `generate_envs.py` no tiene esa opción, haremos lo siguiente:
        # El script `generate_envs.py` ya tiene una lógica de `--force` y sobrescribe.
        # El problema es cómo hacer que el `app_name` coincida con el directorio existente.
        # Si el dir es `staging1`, `prefix` es `staging`, `i` es `1`.
        #
        # Vamos a modificar `get_existing_env_configs` para que devuelva el prefijo y el número.

        # (Volvemos a la lógica original de get_existing_env_configs, pero solo tomamos el nombre)
        # Y llamamos a generate_envs.py para que "genere" ESE nombre específico.
        # Esto requiere que `generate_envs.py` pueda recibir un `target_name`.
        #
        # Como no lo hace, la opción más viable es que el watcher llame a un script
        # que sepa cómo regenerar TODO de una manera predefinida.
        # Por ejemplo, si siempre tienes 10 apps:
        # cmd = ["python", GENERATE_ENVS_SCRIPT, "--prefix", "app", "--count", "10", "--force"]
        # subprocess.run(cmd, check=True)
        #
        # Esto es lo que haremos por ahora, con parámetros configurables en el watcher.
        # El usuario de este script watcher DEBE saber qué parámetros usar para regenerar todo.

        # Parámetros por defecto para regenerar (el usuario debe ajustarlos si es necesario)
        # Estos deberían ser los parámetros que usas normalmente para generar TUS entornos.
        default_prefix = "app"  # O "staging", o lo que uses
        default_count = "3"    # El número total de entornos de ese prefijo

        # Puedes hacer estos configurables con @click.option en el watcher también.
        # Por ahora, los hardcodeamos aquí como ejemplo.
        # Si tienes MÚLTIPLES grupos (ej. 3 staging, 10 app), este enfoque es limitado.

        click.echo(f"Regenerando con: --prefix {default_prefix} --count {default_count} --force")
        cmd_regenerate_all = [
            "python", GENERATE_ENVS_SCRIPT,
            "--prefix", default_prefix,
            "--count", default_count,
            "--out-dir", ENVIRONMENTS_BASE_DIR, # Aseguramos que se usa el dir base correcto
            "--force"
        ]
        # Nota: si `generate_envs.py` también toma `--module-dir`, añádelo.
        # cmd_regenerate_all.extend(["--module-dir", os.path.join(SCRIPT_DIR, "modules", "simulated_app")])


        try:
            # Capturar salida para mejor feedback
            result = subprocess.run(cmd_regenerate_all, check=True, capture_output=True, text=True)
            click.secho(f"Successfully ran generate_envs.py for prefix '{default_prefix}'.", fg="green")
            if result.stdout:
                click.echo("Output:\n" + result.stdout)
            # No necesitamos iterar si regeneramos todo de una vez
            # Así que salimos del bucle de `env_configs` si esta llamada es para "todo".
            # Para este ejemplo simplificado, una sola llamada regenera "todo" basado en default_prefix/count.
            break # Salir del bucle de env_configs
        except subprocess.CalledProcessError as e:
            click.secho(f"Error regenerating environments for prefix '{default_prefix}':", fg="red")
            click.secho(e.stderr, fg="red")
            all_successful = False
            break # Salir del bucle si falla
        except FileNotFoundError:
            click.secho(f"Error: The script '{GENERATE_ENVS_SCRIPT}' was not found.", fg="red")
            all_successful = False
            break


    if all_successful and env_configs: # Solo si hubo configs y la regeneración (única) fue exitosa
        click.secho("All relevant environments regenerated based on default parameters.", fg="green", bold=True)
    elif not env_configs:
        pass # Mensaje ya dado
    else:
        click.secho("Some environments may not have been regenerated correctly.", fg="yellow")


class ModuleChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # Queremos reaccionar a modificaciones en archivos o creación/eliminación en el dir.
        # No reaccionar a eventos sobre el propio directorio raíz del módulo si solo es un 'stat'.
        if event.is_directory:
            # Podríamos querer reaccionar a creación/eliminación de archivos DENTRO del dir
            if isinstance(event, DirModifiedEvent): # Cubre creación/eliminación/renombrado DENTRO
                 click.echo(f"Directory event in module: {event.src_path}")
                 regenerate_environments()
            return
        
        # Reaccionar a modificación de archivos existentes.
        # FileSystemEventHandler también envía eventos para creación, borrado, movido.
        # event.event_type puede ser 'modified', 'created', 'deleted', 'moved'
        if event.event_type in ['modified', 'created', 'deleted', 'moved']:
            click.echo(f"File event in module: {event.event_type} - {event.src_path}")
            # Evitar reaccionar a archivos temporales de algunos editores (ej. .swp, ~)
            if os.path.basename(event.src_path).startswith('.') or \
               os.path.basename(event.src_path).endswith('~') or \
               os.path.basename(event.src_path).endswith('.swp') or \
               os.path.basename(event.src_path).endswith('.swx'):
                click.echo(f"Ignoring temporary file event: {event.src_path}")
                return
            regenerate_environments()


@click.command()
@click.option('--module-path', default=MODULE_DIR_TO_WATCH, help='Directory of the module to watch.', type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('--regen-prefix', default="app", show_default=True, help="Default prefix to use when calling generate_envs.py.")
@click.option('--regen-count', default="3", show_default=True, help="Default count to use when calling generate_envs.py.")
def watch(module_path, regen_prefix, regen_count):
    """
    Watches the specified module directory for changes and regenerates
    all environments using generate_envs.py with the provided
    --regen-prefix and --regen-count.
    """
    global default_prefix, default_count # Para que regenerate_environments() los use
    default_prefix = regen_prefix
    default_count = str(regen_count) # Asegurar que es string para subprocess

    click.secho(f"Watching for changes in module: {module_path}", fg="yellow")
    click.secho(f"On change, will run: python generate_envs.py --prefix {regen_prefix} --count {regen_count} --force", fg="yellow")
    
    event_handler = ModuleChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, module_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        click.echo("\nWatcher stopped by user.")
    observer.join()

if __name__ == "__main__":
    # Inicializar las variables globales que usa regenerate_environments
    # Estos serán sobrescritos por los parámetros de `click` si se ejecuta como comando.
    default_prefix = "app" 
    default_count = "3"
    watch()