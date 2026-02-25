"""Contrato del servicio específico para producto."""

from typing import Protocol, Any, Optional  # Protocol: interfaz estructural.
                                             # Any: tipo comodín. Optional[X]: X | None.


class IServicioProducto(Protocol):
    """Contrato del servicio específico para producto."""
    # Cualquier clase con estos 5 métodos cumple este contrato (duck typing).
    # Los nombres son de NEGOCIO, no de SQL: "listar" (no "select_all").

    # ── OPERACIÓN 1: LISTAR ──────────────────────────────────────────
    async def listar(
        self, esquema: Optional[str] = None,   # Esquema de BD (opcional)
        limite: Optional[int] = None           # Máximo de resultados (opcional)
    ) -> list[dict[str, Any]]:
        ...

    # ── OPERACIÓN 2: BUSCAR POR CÓDIGO ───────────────────────────────
    async def obtener_por_codigo(
        self, codigo: str,                     # PK del producto (ej: "PR001")
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        ...

    # ── OPERACIÓN 3: CREAR ───────────────────────────────────────────
    async def crear(
        self, datos: dict[str, Any],           # Campos del producto
        esquema: Optional[str] = None
    ) -> bool:                                 # True si se creó exitosamente
        ...

    # ── OPERACIÓN 4: ACTUALIZAR ──────────────────────────────────────
    async def actualizar(
        self, codigo: str,                     # PK del producto
        datos: dict[str, Any],                 # Campos a modificar
        esquema: Optional[str] = None
    ) -> int:                                  # Filas afectadas
        ...

    # ── OPERACIÓN 5: ELIMINAR ────────────────────────────────────────
    async def eliminar(
        self, codigo: str,                     # PK del producto
        esquema: Optional[str] = None
    ) -> int:                                  # Filas eliminadas
        ...
