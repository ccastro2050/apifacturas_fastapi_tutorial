"""Contrato para obtener información de conexión a BD."""

from typing import Protocol


class IProveedorConexion(Protocol):
    """Contrato para clases que proveen información de conexión."""

    @property
    def proveedor_actual(self) -> str:
        """Nombre del proveedor activo (ej: 'postgres')."""
        ...

    def obtener_cadena_conexion(self) -> str:
        """Cadena de conexión del proveedor activo."""
        ...
