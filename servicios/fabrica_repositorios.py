"""
fabrica_repositorios.py — Factory centralizada.

Lee DB_PROVIDER del .env y crea el repositorio y servicio correspondientes.
"""
# Patrón FACTORY: crea objetos sin que el controller conozca las clases concretas.

from servicios.conexion.proveedor_conexion import ProveedorConexion  # Lee configuración del .env
from repositorios.producto import RepositorioProductoPostgreSQL      # Repo concreto para PostgreSQL
from servicios.servicio_producto import ServicioProducto              # Servicio de negocio


# =====================================================================
# HELPERS INTERNOS
# =====================================================================

def _obtener_proveedor():
    """Obtiene el proveedor de conexión y su nombre."""
    proveedor = ProveedorConexion()                    # Lee .env vía config.py
    return proveedor, proveedor.proveedor_actual       # Retorna (objeto, "postgres")
# Función privada (_prefijo): solo se usa dentro de este archivo.


def _crear_repo_entidad(repos_por_proveedor: dict, proveedor, nombre: str):
    """Instancia el repositorio específico según el proveedor activo."""
    clase = repos_por_proveedor.get(nombre)            # Busca la clase en el diccionario
    if clase is None:                                  # Proveedor no soportado
        raise ValueError(
            f"Proveedor '{nombre}' no soportado para esta entidad. "
            f"Opciones: {list(repos_por_proveedor.keys())}"
        )
    return clase(proveedor)                            # Crea instancia: Repo(proveedor)
# repos_por_proveedor["postgres"] → RepositorioProductoPostgreSQL
# clase(proveedor) → RepositorioProductoPostgreSQL(proveedor_conexion)


# =====================================================================
# FACTORY DE PRODUCTO
# =====================================================================

_REPOS_PRODUCTO = {
    "postgres": RepositorioProductoPostgreSQL,         # Proveedor → Clase de repositorio
    "postgresql": RepositorioProductoPostgreSQL,       # Alias: mismo repositorio
}
# Para agregar MySQL en el futuro, solo agregas:
#   "mysql": RepositorioProductoMysqlMariaDB,
# ¡Sin tocar NADA más! (principio Open/Closed de SOLID)


def crear_servicio_producto() -> ServicioProducto:
    """Crea el servicio específico de producto."""
    proveedor, nombre = _obtener_proveedor()           # 1. Lee .env → ("postgres")
    repo = _crear_repo_entidad(_REPOS_PRODUCTO, proveedor, nombre)  # 2. Crea repositorio
    return ServicioProducto(repo)                      # 3. Inyecta repo en servicio
# Esta es la ÚNICA función que el controller necesita llamar.
# El controller no sabe qué BD se usa — la fábrica decide todo.
