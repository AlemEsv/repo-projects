# Actividad 23

## Ejercicio 1

1. **Diseño de módulos declarativos**

- _Imagina que has creado tres módulos Terraform: network, compute y storage. Describe cómo diseñarías la interfaz (variables y outputs) de cada uno para que puedan probarse de forma aislada._
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

## Ejercicio 2

## Ejercicio 3

## Ejercicio 4

## Ejercicio 5

## Ejercicio 6

## Ejercicio 7

## Ejercicio 8

## Ejercicio 9

## Ejercicio 10

## Ejercicio 11

## Ejercicio 12
