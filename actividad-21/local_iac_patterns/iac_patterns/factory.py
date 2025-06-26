"""Patrón Factory
----------------
Encapsula la lógica de creación de objetos para recursos Terraform del tipo null_resource.
"""

from typing import Dict, Any
import uuid
from datetime import datetime

class NullResourceFactory:
    """
    Fábrica para crear bloques de recursos `null_resource` en formato Terraform JSON.
    Cada recurso incluye triggers personalizados y valores únicos para garantizar idempotencia.
    """

    @staticmethod
    def create(name: str, triggers: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Crea un bloque de recurso Terraform tipo `null_resource` con triggers personalizados.

        Args:
            name: Nombre del recurso dentro del bloque.
            triggers: Diccionario de valores personalizados que activan recreación del recurso.
                      Si no se proporciona, se inicializa con un UUID y un timestamp.

        Returns:
            Diccionario compatible con la estructura JSON de Terraform para null_resource.
        """
        triggers = triggers or {}

        # Agrega un trigger por defecto: UUID aleatorio para asegurar unicidad
        triggers.setdefault("factory_uuid", str(uuid.uuid4()))

        # Agrega un trigger con timestamp actual en UTC
        triggers.setdefault("timestamp", datetime.utcnow().isoformat())

        # Retorna el recurso estructurado como se espera en archivos .tf.json
        return {
            "resource": [{
                "null_resource": [{
                    name: [{
                        "triggers": triggers
                    }]
                }]
            }]
        }
    
# estructura perecida al nullresourcefactory
class TimestampedNullResourceFactory(NullResourceFactory):
    """
    Fábrica que permite especificar el formato del timestamp para el trigger.
    """

    @staticmethod
    def create(name: str, triggers: Dict[str, Any] | None = None, fmt: str = "%Y-%m-%dT%H:%M:%S") -> Dict[str, Any]:
        """
        Crea un bloque de recurso Terraform tipo `null_resource` con triggers personalizados y timestamp formateado.

        Args:
            name: Nombre del recurso dentro del bloque.
            triggers: Diccionario de valores personalizados que activan recreación del recurso.
            fmt: Formato de fecha y hora para el trigger timestamp.

        Returns:
            Diccionario compatible con la estructura JSON de Terraform para null_resource.
        """
        triggers = triggers or {}

        # Agrega un trigger por defecto: UUID aleatorio para asegurar unicidad
        triggers.setdefault("factory_uuid", str(uuid.uuid4()))

        # Agrega un trigger con timestamp actual en el formato especificado
        triggers.setdefault("timestamp", datetime.utcnow().strftime(fmt))

        # Retorna el recurso estructurado como se espera en archivos .tf.json
        return {
            "resource": [{
                "null_resource": [{
                    name: [{
                        "triggers": triggers
                    }]
                }]
            }]
        }