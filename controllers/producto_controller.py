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

from models.producto import Producto
from servicios.fabrica_repositorios import crear_servicio_producto


router = APIRouter(prefix="/api/producto", tags=["Producto"])


# =========================================================================
# GET /api/producto/ — Listar todos los productos
# =========================================================================

@router.get("/")
async def listar_productos(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todos los productos."""
    try:
        servicio = crear_servicio_producto()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "producto",
            "total": len(filas),
            "datos": filas
        }

    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# GET /api/producto/{codigo} — Obtener producto por código
# =========================================================================

@router.get("/{codigo}")
async def obtener_producto(
    codigo: str,
    esquema: str | None = Query(default=None)
):
    """Obtiene un producto por su código."""
    try:
        servicio = crear_servicio_producto()
        filas = await servicio.obtener_por_codigo(codigo, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró producto con codigo = {codigo}"
            })

        return {
            "tabla": "producto",
            "total": len(filas),
            "datos": filas
        }

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# POST /api/producto/ — Crear producto
# =========================================================================

@router.post("/")
async def crear_producto(
    producto: Producto,
    esquema: str | None = Query(default=None)
):
    """Crea un nuevo producto. Valida con el modelo Pydantic."""
    try:
        datos = producto.model_dump()
        servicio = crear_servicio_producto()
        creado = await servicio.crear(datos, esquema)

        if creado:
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
# PUT /api/producto/{codigo} — Actualizar producto
# =========================================================================

@router.put("/{codigo}")
async def actualizar_producto(
    codigo: str,
    producto: Producto,
    esquema: str | None = Query(default=None)
):
    """Actualiza un producto existente."""
    try:
        datos = producto.model_dump(exclude={"codigo"})
        servicio = crear_servicio_producto()
        filas = await servicio.actualizar(codigo, datos, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Producto actualizado exitosamente.",
                "filtro": f"codigo = {codigo}",
                "filasAfectadas": filas
            }
        else:
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
    codigo: str,
    esquema: str | None = Query(default=None)
):
    """Elimina un producto por su código."""
    try:
        servicio = crear_servicio_producto()
        filas = await servicio.eliminar(codigo, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Producto eliminado exitosamente.",
                "filtro": f"codigo = {codigo}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe producto con codigo = {codigo}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
