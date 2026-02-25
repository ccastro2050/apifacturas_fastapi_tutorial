"""
fabrica_repositorios.py — Factory centralizada.

Lee DB_PROVIDER del .env y crea el repositorio y servicio correspondientes.
"""

from servicios.conexion.proveedor_conexion import ProveedorConexion
from repositorios.producto import RepositorioProductoPostgreSQL
from servicios.servicio_producto import ServicioProducto


# =====================================================================
# HELPERS INTERNOS
# =====================================================================

def _obtener_proveedor():
    """Obtiene el proveedor de conexión y su nombre."""
    proveedor = ProveedorConexion()
    return proveedor, proveedor.proveedor_actual


def _crear_repo_entidad(repos_por_proveedor: dict, proveedor, nombre: str):
    """Instancia el repositorio específico según el proveedor activo."""
    clase = repos_por_proveedor.get(nombre)
    if clase is None:
        raise ValueError(
            f"Proveedor '{nombre}' no soportado para esta entidad. "
            f"Opciones: {list(repos_por_proveedor.keys())}"
        )
    return clase(proveedor)


# =====================================================================
# FACTORY DE PRODUCTO
# =====================================================================

_REPOS_PRODUCTO = {
    "postgres": RepositorioProductoPostgreSQL,
    "postgresql": RepositorioProductoPostgreSQL,
}


def crear_servicio_producto() -> ServicioProducto:
    """Crea el servicio específico de producto."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_PRODUCTO, proveedor, nombre)
    return ServicioProducto(repo)
