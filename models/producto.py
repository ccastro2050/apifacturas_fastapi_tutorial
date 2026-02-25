"""Modelo Pydantic para la tabla producto."""

from pydantic import BaseModel


class Producto(BaseModel):
    """Representa un producto en la base de datos."""
    codigo: str
    nombre: str
    stock: int | None = None
    valorunitario: float | None = None
