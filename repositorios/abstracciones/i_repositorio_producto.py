"""Contrato del repositorio específico para producto."""

from typing import Protocol, Any, Optional  # Protocol: interfaz estructural (duck typing).
                                             # Any: tipo comodín (str, int, Decimal, etc.).
                                             # Optional[X]: equivale a X | None.


class IRepositorioProducto(Protocol):
    """Contrato para el repositorio de producto."""
    # Cualquier clase que tenga estos 5 métodos con estas firmas
    # será reconocida como IRepositorioProducto válido (duck typing).

    # ── OPERACIÓN 1: LISTAR ──────────────────────────────────────────
    async def obtener_todos(
        self,
        esquema: Optional[str] = None,     # Esquema de BD (default "public")
        limite: Optional[int] = None       # Máximo de filas a retornar
    ) -> list[dict[str, Any]]:             # Retorna lista de diccionarios
        """Obtiene todos los productos."""
        ...
    # Ejemplo retorno: [{"codigo": "PR001", "nombre": "Laptop", "stock": 20, ...}]

    # ── OPERACIÓN 2: BUSCAR POR CÓDIGO ───────────────────────────────
    async def obtener_por_codigo(
        self,
        codigo: str,                       # PK del producto (ej: "PR001")
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene un producto por su código."""
        ...
    # Si encuentra: [{"codigo": "PR001", ...}]. Si no: [].

    # ── OPERACIÓN 3: CREAR (INSERT) ──────────────────────────────────
    async def crear(
        self,
        datos: dict[str, Any],             # {"codigo": "PR006", "nombre": "Mouse", ...}
        esquema: Optional[str] = None
    ) -> bool:                             # True si el INSERT afectó al menos 1 fila
        """Crea un nuevo producto. Retorna True si se creó."""
        ...

    # ── OPERACIÓN 4: ACTUALIZAR (UPDATE) ─────────────────────────────
    async def actualizar(
        self,
        codigo: str,                       # PK del producto a actualizar
        datos: dict[str, Any],             # Campos a modificar (sin incluir el código)
        esquema: Optional[str] = None
    ) -> int:                              # Filas afectadas (0 si no encontró)
        """Actualiza un producto. Retorna filas afectadas."""
        ...

    # ── OPERACIÓN 5: ELIMINAR (DELETE) ───────────────────────────────
    async def eliminar(
        self,
        codigo: str,                       # PK del producto a eliminar
        esquema: Optional[str] = None
    ) -> int:                              # Filas eliminadas (0 si no existía)
        """Elimina un producto. Retorna filas eliminadas."""
        ...
