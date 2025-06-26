"""Patrón Composite
Permite tratar múltiples recursos Terraform como una única unidad lógica o módulo compuesto.
"""

from typing import List, Dict, Any

class CompositeModule:
    """
    Clase que agrega múltiples diccionarios de recursos Terraform como un módulo lógico único.
    Sigue el patrón Composite, donde se unifican estructuras individuales en una sola jerarquía.
    """

    def __init__(self) -> None:
        """
        Inicializa la estructura compuesta como una lista vacía de recursos hijos.
        Cada hijo será un diccionario que contiene bloques Terraform.
        """
        self._children: List[Dict[str, Any]] = []

    def add(self, resource_dict: Dict[str, Any]) -> None:
        """
        Agrega un diccionario de recurso (por ejemplo, con una clave 'resource') al módulo.

        Args:
            resource_dict: Diccionario que representa un recurso Terraform.
        """
        self._children.append(resource_dict)

    def export(self) -> Dict[str, Any]:
        """
        Exporta todos los recursos y submódulos agregados en un único diccionario.
        Esta estructura se puede serializar directamente a un archivo Terraform JSON válido.

        Returns:
            Un diccionario con todos los recursos y módulos combinados.
        """
        merged: Dict[str, Any] = {"resource": [], "module": {}}
        for child in self._children:
            if "resource" in child:
                merged["resource"].extend(child.get("resource", []))
            if "module" in child:
                merged["module"].update(child.get("module", {}))
        # Elimina claves vacías para compatibilidad con Terraform
        if not merged["resource"]:
            del merged["resource"]
        if not merged["module"]:
            del merged["module"]
        return merged
