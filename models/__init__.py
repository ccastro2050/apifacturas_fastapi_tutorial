"""
Paquete de modelos Pydantic.

¿Qué es __init__.py?
    Este archivo convierte la carpeta 'models/' en un PAQUETE de Python.
    Sin este archivo, Python no reconoce la carpeta como paquete y
    no puedes hacer imports desde ella.

¿Qué hace el punto (.) en 'from .producto'?
    El punto significa "importación relativa" = "desde ESTA MISMA carpeta".
    .producto → busca el archivo producto.py DENTRO de la carpeta models/.
    Es lo mismo que decir "desde mi carpeta, toma producto.py".

¿Qué logra esta línea?
    Al hacer el import AQUÍ en __init__.py, "re-exportamos" la clase.
    Esto permite que otros archivos usen una ruta más corta:

    SIN esta línea:   from models.producto import Producto  (ruta completa)
    CON esta línea:   from models import Producto           (ruta corta)

    Ambas funcionan, pero la segunda es más limpia.
    Es como crear un "atajo" para que no tengan que escribir la ruta completa.
"""

from .producto import Producto
# from .producto       → desde producto.py (en esta misma carpeta models/)
# import Producto      → trae la clase Producto
# Resultado: quien importe desde 'models' puede acceder a Producto directamente.
