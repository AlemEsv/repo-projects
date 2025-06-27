# Actividad 23

## Ejercicio 1

1. **Diseño de módulos declarativos**

    - _Imagina que has creado tres módulos Terraform: network, compute y storage. Describe cómo diseñarías la interfaz (variables y outputs) de cada uno para que puedan probarse de forma aislada._

        ```yaml
        modules
        ├── network
        │   ├── variables.tf
        │   │   ├── name
        │   │   └── cidr_block
        │   └── outputs.tf
        │       ├── network_id  # red asignada
        │       ├── subnet_ids  # lista de subnets
        │       └── cidr_block  # 10.0.0.0/24
        ├── compute
        │   ├── variables.tf
        │   │   ├── instance_type
        │   │   ├── network_id  # red asignada
        │   │   ├── subnet_id   # subnet especifica
        │   │   └── cidr_block  # 10.0.0.0/24
        │   └── outputs.tf
        │       ├── instance_id # instancia
        │       └── ip_number   # ip asignada
        └── storage
            ├── variables.tf
            │   ├── object_type
            │   └── object_size
            └── outputs.tf
                ├── instance_id # id del objeto
                └── object_info # información general de un objeto guardado
        ```

    - _¿Qué convenios de naming y estructura de outputs pactarías para garantizar, a nivel de contrato, que diferentes equipos puedan reutilizar tus módulos sin integrarlos aún?_

    El contrato debe verificar que las salidas de un módulo sean iguales a las entradas correspondientes de otro módulo que depende de este, y también debe verificar el tipo y cierto formato especifico para la variable en cuestión.

    Contrato: **network -> compute**

    | network (output) | compute (input) | regla |
    | - | - | - |
    | network_id | network_id | string, vpc-* |
    | subnet_ids[0] | subnet_id | string, subnet-* |
    | cidr_block | cidr_block | string, x.x.x.x/x |

    Para validar las convenciones de naming entre network y compute, podemos aplicar análisis estático con pruebas unitarias de pytest y una fixture compartida que modele la salida esperada de network, así como un test que valide que compute use el mismo prefijo de nombre. Así, si compute cambia el patrón de nombre esperado, la prueba falla antes del despliegue.

    De esta forma, un equipo puede trabajar solo con la fixture de network (sin el módulo real) y validar su módulo compute.Así procederíamos de forma análoga sobre el contrato **compute -> storage**.

2. **Caso límite sin recursos externos**

    Caso 1: **Máscara CIDR fuera de rango**

    ```python
    # Ejemplo de input inválido en módulo network
    variable "vpc_cidr" {
    type        = string
    description = "Bloque CIDR"
    }

    # Test cases inválidos:
    # - "10.0.0.0/33" (máscara > 32)
    # - "256.0.0.0/16" (octeto > 255)
    # - "10.0.0.0/-1" (máscara negativa)
    ```

    Caso 2: **Número de instancias cero o negativo**

    ```python
    # Ejemplo de input inválido en módulo compute
    variable "instance_count" {
    type        = number
    description = "numero de instancias"
    validation {
        condition     = var.instance_count > 0 && var.instance_count <= 5
        error_message = "La cantidad de instancia debe estar entre 1 y 5"
    }
    }

    # Test casos inválidos:
    # - 0 (sin instancias)
    # - -5 (número negativo)
    # - 10 (excede límite máximo)
    ```

    Validación de sintaxis

    ```python
    # 1. Formato y sintaxis básica
    terraform fmt -check -diff
    terraform validate

    # 2. Validación de variables con valores específicos
    terraform plan -var="vpc_cidr=10.0.0.0/33"
    ```

    Herramientas de validación de sintaxis:

    - `terraform fmt -check`: Valida formato y convenciones de código

    - `terraform validate`: Detecta errores de sintaxis y referencias inválidas

    - `terraform plan -refresh=false`: Validación semántica sin consultar estado real

    - `terraform output -json`: Verificación de contratos mediante análisis programático

3. **Métrica de cobertura de contrato**

   * Plantea un método para cuantificar qué porcentaje de tu contrato (outputs documentados) está siendo validado por los contract tests.
   * ¿Cómo balancearías la exhaustividad (todos los campos) con el costo de mantenimiento (cambios frecuentes en outputs)?

## Ejercicio 2

## Ejercicio 3

## Ejercicio 4

## Ejercicio 5

## Ejercicio 6

1. **Deuda técnica en pruebas IaC**

2. **Documentación viva de tests**

    Un formato para documentación viva de tests es una tabla en Markdown con diagramas simples:

    ```txt
    | Módulo   | Output/Contrato         | Test asociado                | Tipo de test      |
    |----------|------------------------|------------------------------|-------------------|
    | network  | network_id (string)    | test_network_contract.py     | Contract/Unit     |
    | network  | subnet_ids (list)      | test_network_contract.py     | Contract/Unit     |
    | compute  | instance_id (string)   | test_compute_integration.py  | Integración       |
    | storage  | bucket_name (string)   | test_storage_contract.py     | Contract/Unit     |
    ```

    Diagramas: Se puede utilizar **Mermaid** para visualizar cómo se conectan los módulos y qué tests cubren cada relación o **DOT** con **terraform**.

3. **Automatización local de la suite**

    Script `run_all.sh`:

    - **Limpieza previa**:

        Se ejecuta `terraform destroy -auto-approve` para eliminar cualquier recurso o estado previo.

    - **Ejecución de fases**:

        El script ejecuta cada grupo de pruebas:

        - Primero los tests unitarios (`pytest pruebas_unitarias/`).

        - Luego los tests de contrato y smoke (`pytest pruebas_contrato/`).

        - Después los tests de integración (`pytest pruebas_integracion/` o scripts específicos).

        - Finalmente los tests extremo a extremo (E2E), que pueden ser scripts que levanten contenedores y hagan peticiones HTTP.

        ```bash
        #!/bin/bash
        # 1. Limpieza previa
        terraform destroy -auto-approve

        # 2. Ejecutar pruebas unitarias
        pytest pruebas_unitarias/ > unit.log
        # 3. Ejecutar pruebas de contrato/smoke
        python check_contracts.py > contract.log
        # 4. Ejecutar pruebas de integración
        pytest pruebas_integracion/ > integration.log
        # 5. Ejecutar pruebas E2E
        python e2e_test.py > e2e.log

        # 6. Resumir resultados
        echo "Resumen de pruebas:"
        echo "Unitarias: $(grep -c 'PASSED' unit.log) pasaron, $(grep -c 'FAILED' unit.log) fallaron"
        echo "Contrato: $(grep -c 'OK' contract.log) pasaron, $(grep -c 'FAIL' contract.log) fallaron"
        echo "Integración: $(grep -c 'PASSED' integration.log) pasaron, $(grep -c 'FAILED' integration.log) fallaron"
        echo "E2E: $(grep -c 'OK' e2e.log) pasaron, $(grep -c 'FAIL' e2e.log) fallaron"
        ```

## Ejercicio 7

## Ejercicio 8

## Ejercicio 9

## Ejercicio 10

## Ejercicio 11

## Ejercicio 12
