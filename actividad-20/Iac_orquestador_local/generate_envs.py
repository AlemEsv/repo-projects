import click
import os
import json
from shutil import copyfile
from jsonschema import validate, ValidationError # Importar

# --- Definiciones de Schema (pegar MAIN_TF_SCHEMA y NETWORK_TF_SCHEMA/GENERIC_TERRAFORM_FILE_SCHEMA aquí) ---
MAIN_TF_SCHEMA = {
    "type": "object",
    "properties": {
        "variable": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "const": "string"},
                        "description": {"type": "string"},
                        "default": {"type": "string"}
                    },
                    "required": ["type", "default"],
                    "additionalProperties": False
                },
                "network": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "const": "string"},
                        "description": {"type": "string"},
                        "default": {"type": "string"}
                    },
                    "required": ["type", "default"],
                    "additionalProperties": False
                }
            },
            "required": ["name", "network"],
            "additionalProperties": False 
        },
        "resource": {
            "type": "object",
            "properties": {
                "null_resource": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z0-9_.-]+$": { 
                            "type": "object",
                            "properties": {
                                "triggers": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "network": {"type": "string"}
                                    },
                                    "required": ["name", "network"],
                                    "additionalProperties": False
                                },
                                "provisioner": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "local-exec": {
                                                "type": "object",
                                                "properties": {
                                                    "command": {"type": "string"}
                                                },
                                                "required": ["command"],
                                                "additionalProperties": False
                                            }
                                        },
                                        "additionalProperties": False
                                    },
                                    "minItems": 1,
                                    "maxItems": 1 
                                }
                            },
                            "required": ["triggers", "provisioner"],
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False 
                }
            },
            "required": ["null_resource"],
            "additionalProperties": True 
        }
    },
    "required": ["variable", "resource"],
    "additionalProperties": True 
}

GENERIC_TERRAFORM_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "variable": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                    "default": {} 
                },
                "required": ["type"] 
            }
        },
        "locals": {"type": "object"},
        "resource": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "additionalProperties": {"type": "object"}
            }
        },
        "data": { 
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "additionalProperties": {"type": "object"}
            }
        },
        "output": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "value": {}, 
                    "description": {"type": "string"},
                    "sensitive": {"type": "boolean"}
                },
                "required": ["value"]
            }
        },
        "module": {
             "type": "object",
             "additionalProperties": { 
                 "type": "object",
                 "properties": {
                     "source": {"type": "string"}
                 },
                 "required": ["source"]
             }
        },
        "terraform": {"type": "object"}, 
        "provider": { 
             "type": "object",
             "additionalProperties": {"type": "object"} 
        }
    },
    "additionalProperties": False
}
NETWORK_TF_SCHEMA = GENERIC_TERRAFORM_FILE_SCHEMA
# --- Fin de Definiciones de Schema ---


def get_main_tf_content_corrected(app_name):
    command_string = f"echo 'Arrancando servidor ${{var.name}} en red ${{var.network}}'"
    return {
        "variable": { 
            "name": {
                "type": "string",
                "description": "Name for the application/server.",
                "default": app_name 
            },
            "network": {
                "type": "string",
                "description": "Network identifier for the application/server.",
                "default": "default-network" 
            }
        },
        "resource": { 
            "null_resource": { 
                app_name: { 
                    "triggers": {
                        "name":    "${var.name}",
                        "network": "${var.network}"
                    },
                    "provisioner": [
                        {
                            "local-exec": {
                                "command": command_string
                            }
                        }
                    ]
                }
            }
        }
    }


@click.command()
@click.option(
    '--count',
    type=int,
    required=True,
    help='Number of environment directories to generate.'
)
@click.option(
    '--prefix',
    default='app',
    show_default=True,
    help='Prefix for the environment directory names (e.g., "staging" -> staging1, staging2).'
)
@click.option(
    '--module-dir',
    default='modules/simulated_app',
    show_default=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    help='Path to the Terraform module directory (for copying network.tf.json).'
)
@click.option(
    '--out-dir',
    default='environments',
    show_default=True,
    type=click.Path(resolve_path=True),
    help='The base directory where environment subdirectories will be created.'
)
@click.option(
    '--force',
    is_flag=True,
    help='Overwrite existing environment directories without asking.'
)
def generate_envs(count, prefix, module_dir, out_dir, force):
    """
    Generates multiple Terraform environment directories with JSON schema validation.
    """
    click.echo(f"Starting generation of {count} environments with prefix '{prefix}'...")
    
    # No necesitamos resolver rutas aquí si usamos resolve_path=True en click.option
    # out_dir_abs = out_dir
    # module_dir_abs = module_dir

    if not os.path.exists(out_dir): # out_dir ya es absoluto por resolve_path
        try:
            os.makedirs(out_dir)
            click.echo(f"Created base output directory: {out_dir}")
        except OSError as e:
            click.secho(f"Error creating base output directory {out_dir}: {e}", fg="red")
            return

    source_network_tf = os.path.join(module_dir, "network.tf.json") # module_dir ya es absoluto
    if not os.path.exists(source_network_tf):
        click.secho(f"Error: Source network.tf.json not found at {source_network_tf}", fg="red")
        click.echo("Please ensure --module-dir points to a directory containing network.tf.json.")
        return

    # Validar network.tf.json del módulo UNA VEZ antes del bucle
    try:
        with open(source_network_tf, 'r') as f:
            network_content_to_validate = json.load(f)
        validate(instance=network_content_to_validate, schema=NETWORK_TF_SCHEMA)
        click.echo(f"Source '{source_network_tf}' is valid against its schema.")
    except json.JSONDecodeError as e:
        click.secho(f"Error: Source '{source_network_tf}' is not valid JSON: {e}", fg="red")
        return
    except ValidationError as e:
        click.secho(f"Error: Source '{source_network_tf}' failed schema validation:", fg="red")
        click.secho(f"  Path: {e.path}", fg="red")
        click.secho(f"  Message: {e.message}", fg="red")
        return
    except Exception as e: # Otras excepciones al leer/validar
        click.secho(f"Error processing source '{source_network_tf}': {e}", fg="red")
        return


    generated_count = 0
    for i in range(1, count + 1):
        app_name = f"{prefix}{i}"
        env_dir_path = os.path.join(out_dir, app_name)

        click.echo(f"\nProcessing environment: {app_name}")

        if os.path.exists(env_dir_path):
            if not force:
                if not click.confirm(f"Directory '{env_dir_path}' already exists. Overwrite contents?"):
                    click.echo(f"Skipping '{app_name}'.")
                    continue
            click.echo(f"Overwriting contents in existing directory: {env_dir_path}")
        else:
            try:
                os.makedirs(env_dir_path)
                click.echo(f"Created directory: {env_dir_path}")
            except OSError as e:
                click.secho(f"Error creating directory {env_dir_path}: {e}", fg="red")
                continue

        # 1. Generar y validar main.tf.json
        main_content = get_main_tf_content_corrected(app_name)
        main_tf_path = os.path.join(env_dir_path, 'main.tf.json')
        try:
            validate(instance=main_content, schema=MAIN_TF_SCHEMA)
            click.echo(f"  Content for 'main.tf.json' is valid against its schema.")
            with open(main_tf_path, 'w') as fp:
                json.dump(main_content, fp, sort_keys=True, indent=4)
            click.echo(f"  Generated: {main_tf_path}")
        except ValidationError as e:
            click.secho(f"  Error: Generated 'main.tf.json' content for {app_name} failed schema validation. Skipping file write.", fg="red")
            click.secho(f"    Path: {e.path}", fg="red") # Muestra la ruta dentro del JSON donde falló
            click.secho(f"    Message: {e.message}", fg="red")
            # Descomenta para ver el JSON que falló (puede ser largo)
            # click.secho(f"    Problematic JSON data:\n{json.dumps(e.instance, indent=2)}", fg="yellow")
            continue # Pasar al siguiente entorno si este falla
        except IOError as e:
            click.secho(f"  Error writing {main_tf_path}: {e}", fg="red")
            continue


        # 2. Copiar network.tf.json (ya validado antes del bucle)
        dest_network_tf = os.path.join(env_dir_path, "network.tf.json")
        try:
            copyfile(source_network_tf, dest_network_tf)
            click.echo(f"  Copied: {source_network_tf} to {dest_network_tf}")
        except IOError as e:
            click.secho(f"  Error copying network.tf.json: {e}", fg="red")
            continue # Si falla la copia, no se cuenta como generado.

        generated_count +=1


    if generated_count > 0:
        click.secho(f"\nSuccessfully generated/updated {generated_count} environment(s) in '{out_dir}'.", fg="green")
    else:
        click.echo("\nNo environments were generated or updated that passed validation.")


if __name__ == "__main__":
    generate_envs()