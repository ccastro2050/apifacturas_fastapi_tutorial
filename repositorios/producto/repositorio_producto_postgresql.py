"""Repositorio de producto para PostgreSQL."""

from repositorios.base_repositorio_postgresql import BaseRepositorioPostgreSQL
# Importa la clase base que tiene toda la lógica SQL genérica.
# Al heredar de ella, obtenemos los 5 métodos protegidos (_obtener_filas, etc.).


class RepositorioProductoPostgreSQL(BaseRepositorioPostgreSQL):
    """Acceso a datos de producto en PostgreSQL."""
    # Hereda de BaseRepositorioPostgreSQL → tiene toda la lógica SQL.
    # No necesita constructor: usa el del padre (recibe proveedor_conexion).

    TABLA = "producto"                     # Nombre de la tabla en la BD
    CLAVE_PRIMARIA = "codigo"              # Nombre de la columna PK

    # ── OPERACIÓN 1: LISTAR ──────────────────────────────────────────
    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todos los productos."""
        return await self._obtener_filas(self.TABLA, esquema, limite)
    # Delega a la clase base → SELECT * FROM "public"."producto" LIMIT 1000

    # ── OPERACIÓN 2: BUSCAR POR CÓDIGO ───────────────────────────────
    async def obtener_por_codigo(self, codigo, esquema=None):
        """Obtiene un producto por su codigo."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )
    # str(codigo): convierte a string por seguridad.
    # → SELECT * FROM "public"."producto" WHERE "codigo" = :valor

    # ── OPERACIÓN 3: CREAR ───────────────────────────────────────────
    async def crear(self, datos, esquema=None):
        """Crea un nuevo producto."""
        return await self._crear(self.TABLA, datos, esquema)
    # datos: {"codigo": "PR006", "nombre": "Mouse", "stock": 10, ...}
    # → INSERT INTO "public"."producto" ("codigo", ...) VALUES (:codigo, ...)

    # ── OPERACIÓN 4: ACTUALIZAR ──────────────────────────────────────
    async def actualizar(self, codigo, datos, esquema=None):
        """Actualiza un producto existente."""
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), datos, esquema
        )
    # → UPDATE "public"."producto" SET ... WHERE "codigo" = :valor_clave

    # ── OPERACIÓN 5: ELIMINAR ────────────────────────────────────────
    async def eliminar(self, codigo, esquema=None):
        """Elimina un producto por su codigo."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )
    # → DELETE FROM "public"."producto" WHERE "codigo" = :valor_clave
