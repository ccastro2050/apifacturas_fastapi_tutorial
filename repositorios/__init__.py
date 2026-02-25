"""
Paquete de repositorios — Clase base de PostgreSQL.

¿Qué es __init__.py?
    Este archivo convierte la carpeta 'repositorios/' en un PAQUETE de Python.
    Sin este archivo, Python no reconoce la carpeta como paquete.

¿Qué hace el punto (.) en 'from .base_repositorio_postgresql'?
    El punto significa "importación relativa" = "desde ESTA MISMA carpeta".
    .base_repositorio_postgresql → busca base_repositorio_postgresql.py
    DENTRO de la carpeta repositorios/.

¿Qué logra esta línea?
    Re-exporta la clase para permitir una ruta de import más corta:

    SIN esta línea:   from repositorios.base_repositorio_postgresql import BaseRepositorioPostgreSQL
    CON esta línea:   from repositorios import BaseRepositorioPostgreSQL
"""

from .base_repositorio_postgresql import BaseRepositorioPostgreSQL
# from .base_repositorio_postgresql  → desde base_repositorio_postgresql.py (esta carpeta)
# import BaseRepositorioPostgreSQL   → trae la clase base
