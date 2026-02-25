"""
main.py — Punto de entrada de la API REST con FastAPI.

Este archivo es el PRIMER archivo que se ejecuta al iniciar la aplicación.
Su responsabilidad es:
1. Crear la instancia de FastAPI (la "aplicación" web)
2. Registrar los routers (controladores) que manejan las rutas HTTP
3. Definir el endpoint raíz (/) para verificación rápida

Ejecutar con: uvicorn main:app --reload

En el proyecto completo (ApiFacturasFastApi_Crud), este archivo registra
13 routers para 12 tablas + 1 controller genérico. En este tutorial,
solo registramos 1 router: el de producto.
"""

# ─── Imports ─────────────────────────────────────────────────────────

from fastapi import FastAPI          # FastAPI: clase principal del framework.
                                     # Crear una instancia de FastAPI() es crear
                                     # la aplicación web completa. Esta instancia:
                                     # - Recibe peticiones HTTP (GET, POST, PUT, DELETE)
                                     # - Las enruta al handler correcto
                                     # - Genera documentación automática (Swagger UI)

from controllers.producto_controller import router as producto_router
# Importa el router (grupo de rutas) del controller de producto.
# "router as producto_router" → renombra para claridad.
# Este router contiene 5 endpoints:
#   GET    /api/producto/         → Listar todos
#   GET    /api/producto/{codigo} → Obtener uno
#   POST   /api/producto/         → Crear
#   PUT    /api/producto/{codigo} → Actualizar
#   DELETE /api/producto/{codigo} → Eliminar


# ─── Crear la aplicación FastAPI ─────────────────────────────────────

app = FastAPI(                       # Crea la instancia principal de la aplicación.
    title="API Producto - Tutorial FastAPI",
                                     # title: nombre que aparece en Swagger UI (/docs).
    description="API REST CRUD para la tabla producto. Tutorial con arquitectura de 3 capas.",
                                     # description: texto descriptivo en la documentación.
    version="1.0.0",                 # version: versión de la API mostrada en /docs.
)
# app es el objeto que uvicorn busca: "uvicorn main:app"
#   main  → archivo main.py
#   app   → variable app dentro de main.py


# ─── Registrar controladores ────────────────────────────────────────

app.include_router(producto_router)  # Registra TODAS las rutas del router de producto.
# include_router() toma el APIRouter del controller y lo "monta" en la app.
# Después de esta línea, la app conoce los 5 endpoints de /api/producto/.
# El prefix="/api/producto" y tags=["Producto"] vienen del controller.
#
# En el proyecto completo, aquí habría 13 líneas include_router(),
# una por cada controller. En este tutorial, solo necesitamos una.


# ─── Endpoint raíz ──────────────────────────────────────────────────

@app.get("/", tags=["Root"])         # Registra un GET en la raíz (/).
                                     # tags=["Root"] lo agrupa bajo "Root" en Swagger UI.
async def root():                    # async: handler asíncrono (no bloquea el servidor).
    """Endpoint raíz de verificación."""
    return {                         # FastAPI convierte este dict a JSON automáticamente.
        "mensaje": "API Producto - Tutorial FastAPI activa.",
                                     # Mensaje de confirmación de que la API está corriendo.
        "documentacion": "/docs",    # URL de Swagger UI (documentación interactiva).
        "documentacion_alternativa": "/redoc"
                                     # URL de ReDoc (documentación alternativa, solo lectura).
    }
# Este endpoint sirve para verificar rápidamente que la API está activa.
# Al visitar http://localhost:8000/ se ve el JSON de respuesta.
