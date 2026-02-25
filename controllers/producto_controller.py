"""
producto_controller.py — Controller específico para la tabla producto.

Endpoints:
- GET    /api/producto/              → Listar productos
- GET    /api/producto/{codigo}      → Obtener producto por código
- POST   /api/producto/              → Crear producto
- PUT    /api/producto/{codigo}      → Actualizar producto
- DELETE /api/producto/{codigo}      → Eliminar producto
"""

from fastapi import APIRouter, HTTPException, Query, Response
# APIRouter: crea grupo de rutas con prefijo común (mini app).
# HTTPException: lanza errores HTTP (404, 500, etc.).
# Query: define parámetros de query string (?esquema=public&limite=10).
# Response: respuestas HTTP personalizadas (ej: 204 sin body).

from models.producto import Producto   # Modelo Pydantic: valida el body de POST y PUT
from servicios.fabrica_repositorios import crear_servicio_producto  # Factory: crea el servicio


router = APIRouter(prefix="/api/producto", tags=["Producto"])
# prefix: todas las rutas empiezan con /api/producto
# tags: agrupa endpoints bajo "Producto" en Swagger UI


# =========================================================================
# GET /api/producto/ — Listar todos los productos
# =========================================================================

@router.get("/")                       # Registra esta función como handler de GET /api/producto/
async def listar_productos(
    esquema: str | None = Query(default=None),   # Query string opcional: ?esquema=public
    limite: int | None = Query(default=None)      # Query string opcional: ?limite=10
):
    """Lista todos los productos."""
    try:
        servicio = crear_servicio_producto()      # Factory: crea todo el stack (repo + servicio)
        filas = await servicio.listar(esquema, limite)  # Delega al servicio → repo → SQL

        if len(filas) == 0:
            return Response(status_code=204)       # 204 No Content: sin productos
        # 204 = "petición exitosa pero no hay contenido que devolver"

        return {                                   # FastAPI convierte dict a JSON automáticamente
            "tabla": "producto",
            "total": len(filas),
            "datos": filas
        }

    except ValueError as ex:                       # ValueError: validación del servicio
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": str(ex)
        })
    except Exception as ex:                        # Cualquier otro error (BD, conexión, etc.)
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# GET /api/producto/{codigo} — Obtener producto por código
# =========================================================================

@router.get("/{codigo}")               # {codigo} = path parameter: GET /api/producto/PR001
async def obtener_producto(
    codigo: str,                       # Viene de la URL (path parameter)
    esquema: str | None = Query(default=None)
):
    """Obtiene un producto por su código."""
    try:
        servicio = crear_servicio_producto()
        filas = await servicio.obtener_por_codigo(codigo, esquema)

        if len(filas) == 0:                        # Producto no encontrado
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró producto con codigo = {codigo}"
            })
        # 404 Not Found = "el recurso que buscas no existe"

        return {
            "tabla": "producto",
            "total": len(filas),
            "datos": filas
        }

    except HTTPException:
        raise                                      # Re-lanza 404 sin convertirla en 500
    # Sin este bloque, except Exception capturaría el 404 y lo haría 500.
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# POST /api/producto/ — Crear producto
# =========================================================================

@router.post("/")
async def crear_producto(
    producto: Producto,                # Body JSON validado por Pydantic automáticamente
    esquema: str | None = Query(default=None)
):
    """Crea un nuevo producto. Valida con el modelo Pydantic."""
    # Si el JSON es inválido, FastAPI retorna 422 SIN ejecutar esta función.
    try:
        datos = producto.model_dump()              # Pydantic → dict Python
        # {"codigo": "PR006", "nombre": "Mouse", "stock": 10, "valorunitario": 50000.0}

        servicio = crear_servicio_producto()
        creado = await servicio.crear(datos, esquema)  # Servicio valida → repo ejecuta INSERT

        if creado:                                 # INSERT afectó al menos 1 fila
            return {
                "estado": 200,
                "mensaje": "Producto creado exitosamente.",
                "datos": datos
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear el producto."
            })

    except HTTPException:
        raise                                      # Re-lanza sin modificar
    except ValueError as ex:                       # Validación del servicio
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Datos inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# PUT /api/producto/{codigo} — Actualizar producto
# =========================================================================

@router.put("/{codigo}")
async def actualizar_producto(
    codigo: str,                       # De la URL: PUT /api/producto/PR001
    producto: Producto,                # Body JSON validado por Pydantic
    esquema: str | None = Query(default=None)
):
    """Actualiza un producto existente."""
    try:
        datos = producto.model_dump(exclude={"codigo"})  # Excluye PK del SET
        # exclude={"codigo"}: no queremos que UPDATE cambie la PK.
        # Resultado: {"nombre": "Laptop Gamer", "stock": 15, "valorunitario": 3000000.0}

        servicio = crear_servicio_producto()
        filas = await servicio.actualizar(codigo, datos, esquema)
        # UPDATE producto SET ... WHERE codigo = 'PR001'

        if filas > 0:                              # Producto existía y se actualizó
            return {
                "estado": 200,
                "mensaje": "Producto actualizado exitosamente.",
                "filtro": f"codigo = {codigo}",
                "filasAfectadas": filas
            }
        else:                                      # filas == 0: producto no existe
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe producto con codigo = {codigo}"
            })

    except HTTPException:
        raise
    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Datos inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# DELETE /api/producto/{codigo} — Eliminar producto
# =========================================================================

@router.delete("/{codigo}")
async def eliminar_producto(
    codigo: str,                       # De la URL: DELETE /api/producto/PR001
    esquema: str | None = Query(default=None)
):
    """Elimina un producto por su código."""
    # DELETE no necesita body — solo el identificador en la URL.
    try:
        servicio = crear_servicio_producto()
        filas = await servicio.eliminar(codigo, esquema)
        # DELETE FROM producto WHERE codigo = 'PR001'

        if filas > 0:                              # Producto existía y se eliminó
            return {
                "estado": 200,
                "mensaje": "Producto eliminado exitosamente.",
                "filtro": f"codigo = {codigo}",
                "filasEliminadas": filas
            }
        else:                                      # filas == 0: producto no existía
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe producto con codigo = {codigo}"
            })

    except HTTPException:
        raise                                      # Re-lanza 404
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
