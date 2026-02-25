"""
Repositorios específicos de producto.

¿Qué hace el punto (.) en 'from .repositorio_producto_postgresql'?
    El punto significa "importación relativa" = "desde ESTA MISMA carpeta".
    .repositorio_producto_postgresql → busca repositorio_producto_postgresql.py
    DENTRO de la carpeta repositorios/producto/.

¿Qué logra esta línea?
    Re-exporta la clase para permitir una ruta de import más corta:

    SIN esta línea:   from repositorios.producto.repositorio_producto_postgresql import RepositorioProductoPostgreSQL
    CON esta línea:   from repositorios.producto import RepositorioProductoPostgreSQL
"""

from .repositorio_producto_postgresql import RepositorioProductoPostgreSQL
# from .repositorio_producto_postgresql  → desde repositorio_producto_postgresql.py (esta carpeta)
# import RepositorioProductoPostgreSQL   → trae la clase concreta de producto
