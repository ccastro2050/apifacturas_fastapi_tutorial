"""Contrato del repositorio específico para producto."""
from typing import Protocol, Any, Optional


class IRepositorioProducto(Protocol):
    """Contrato para el repositorio de producto."""

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todos los productos."""
        ...

    async def obtener_por_codigo(
        self,
        codigo: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene un producto por su código."""
        ...

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea un nuevo producto. Retorna True si se creó."""
        ...

    async def actualizar(
        self,
        codigo: str,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        """Actualiza un producto. Retorna filas afectadas."""
        ...

    async def eliminar(
        self,
        codigo: str,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina un producto. Retorna filas eliminadas."""
        ...
