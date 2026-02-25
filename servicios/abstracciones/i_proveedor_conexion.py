"""Contrato para obtener información de conexión a BD."""

from typing import Protocol          # Protocol: clase base para interfaces estructurales (duck typing).
                                      # Si una clase tiene los mismos métodos, cumple el contrato
                                      # sin necesidad de heredar explícitamente.


class IProveedorConexion(Protocol):
    """Contrato para clases que proveen información de conexión."""
    # La "I" al inicio es convención: indica que es una Interface.
    # Heredar de Protocol la convierte en interfaz estructural.

    @property
    def proveedor_actual(self) -> str:
        """Nombre del proveedor activo (ej: 'postgres')."""
        ...                           # "..." (Ellipsis) = sin implementación, solo la firma.
    # @property: se accede como atributo, sin paréntesis.
    # → str: debe retornar un string con el nombre del proveedor.

    def obtener_cadena_conexion(self) -> str:
        """Cadena de conexión del proveedor activo."""
        ...
    # Retorna la cadena completa, ej: "postgresql+asyncpg://postgres:...@localhost:5432/bd"
