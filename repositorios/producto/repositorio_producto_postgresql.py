"""Repositorio de producto para PostgreSQL."""

from repositorios.base_repositorio_postgresql import BaseRepositorioPostgreSQL


class RepositorioProductoPostgreSQL(BaseRepositorioPostgreSQL):
    """Acceso a datos de producto en PostgreSQL."""

    TABLA = "producto"
    CLAVE_PRIMARIA = "codigo"

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todos los productos."""
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_codigo(self, codigo, esquema=None):
        """Obtiene un producto por su codigo."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )

    async def crear(self, datos, esquema=None):
        """Crea un nuevo producto."""
        return await self._crear(self.TABLA, datos, esquema)

    async def actualizar(self, codigo, datos, esquema=None):
        """Actualiza un producto existente."""
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), datos, esquema
        )

    async def eliminar(self, codigo, esquema=None):
        """Elimina un producto por su codigo."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )
