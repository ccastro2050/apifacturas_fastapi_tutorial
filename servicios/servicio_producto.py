"""Servicio específico para la entidad producto."""
# Capa de negocio: validaciones, normalización de parámetros y delegación al repositorio.

from typing import Any                # Any: tipo comodín para dict[str, Any].


class ServicioProducto:
    """Lógica de negocio para producto."""
    # NO hereda de IServicioProducto. Cumple el contrato por duck typing.

    def __init__(self, repositorio):
        if repositorio is None:                            # Validación: fail fast
            raise ValueError("repositorio no puede ser None.")
        self._repo = repositorio                           # Guarda referencia (atributo privado)
    # repositorio: puede ser PostgreSQL, MySQL o un mock para pruebas.
    # Inversión de Dependencias: depende de la abstracción, no de la implementación.

    # ── OPERACIÓN 1: LISTAR ──────────────────────────────────────────
    async def listar(self, esquema: str | None = None, limite: int | None = None) -> list[dict[str, Any]]:
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        # Normaliza: "  public  " → "public", "  " → None, None → None.
        limite_norm = limite if limite and limite > 0 else None
        # Normaliza: 50 → 50, 0 → None, -5 → None, None → None.
        return await self._repo.obtener_todos(esquema_norm, limite_norm)
        # Delega al repositorio. El servicio NO ejecuta SQL.

    # ── OPERACIÓN 2: BUSCAR POR CÓDIGO ───────────────────────────────
    async def obtener_por_codigo(self, codigo: str, esquema: str | None = None) -> list[dict[str, Any]]:
        if not codigo or not codigo.strip():               # Validación de negocio
            raise ValueError("El código no puede estar vacío.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.obtener_por_codigo(codigo, esquema_norm)

    # ── OPERACIÓN 3: CREAR ───────────────────────────────────────────
    async def crear(self, datos: dict[str, Any], esquema: str | None = None) -> bool:
        if not datos:                                      # None, {} o vacío
            raise ValueError("Los datos no pueden estar vacíos.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.crear(datos, esquema_norm)
    # La validación de TIPOS la hace Pydantic en el controller.
    # El servicio solo valida que los datos no estén vacíos.

    # ── OPERACIÓN 4: ACTUALIZAR ──────────────────────────────────────
    async def actualizar(self, codigo: str, datos: dict[str, Any], esquema: str | None = None) -> int:
        if not codigo or not codigo.strip():               # ¿Qué producto actualizar?
            raise ValueError("El código no puede estar vacío.")
        if not datos:                                      # ¿Qué cambiar?
            raise ValueError("Los datos no pueden estar vacíos.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.actualizar(codigo, datos, esquema_norm)

    # ── OPERACIÓN 5: ELIMINAR ────────────────────────────────────────
    async def eliminar(self, codigo: str, esquema: str | None = None) -> int:
        if not codigo or not codigo.strip():
            raise ValueError("El código no puede estar vacío.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.eliminar(codigo, esquema_norm)
