# PARTE 5: Capa de Presentación — Modelo Pydantic y Controller

> En esta parte construimos la **capa más alta** de la arquitectura: el modelo Pydantic que valida los datos de entrada y el controller que expone los 5 endpoints HTTP. Esta es la capa que el cliente (Postman, Swagger UI, frontend) ve directamente.

> **Nota:** Si ya tienes experiencia con FastAPI y Pydantic, puedes ir directamente al **Resumen** al final de esta parte.

---

## 5.1 ¿Qué es Pydantic y por qué lo usamos?

**Pydantic** es una librería de validación de datos. Cuando un cliente envía un JSON a la API, Pydantic verifica automáticamente que los datos tengan el tipo correcto **antes** de que lleguen a tu código.

### Ejemplo sin Pydantic vs con Pydantic:

**Sin Pydantic (validación manual):**
```python
@router.post("/")
async def crear_producto(request: Request):
    body = await request.json()          # ← JSON crudo, sin validar
    if "codigo" not in body:             # ← validación manual
        raise HTTPException(400, "Falta codigo")
    if not isinstance(body["stock"], int):  # ← más validación manual
        raise HTTPException(400, "stock debe ser entero")
    # ... y así por cada campo
```

**Con Pydantic (validación automática):**
```python
@router.post("/")
async def crear_producto(producto: Producto):  # ← Pydantic valida automáticamente
    datos = producto.model_dump()               # ← datos ya validados y tipados
```

Si el cliente envía `{"stock": "abc"}`, Pydantic rechaza la petición con error **422 Unprocessable Entity** antes de que tu código se ejecute. No necesitas escribir ni una línea de validación.

### Comparación con otros frameworks:

| Framework | Validación de datos |
|-----------|-------------------|
| **FastAPI + Pydantic** | Automática: defines el modelo y Pydantic valida |
| **ASP.NET** | Data Annotations (`[Required]`, `[Range]`) en los modelos |
| **Spring Boot** | Jakarta Validation (`@NotNull`, `@Min`) en los DTOs |
| **Express.js** | Manual o con librerías como Joi/Zod |

---

## 5.2 Modelo `Producto` — Validación de datos de entrada

Este archivo define la **estructura** de un producto. FastAPI usa este modelo para:
1. **Validar** que el JSON tenga los campos correctos con los tipos correctos
2. **Documentar** automáticamente en Swagger UI qué espera cada endpoint
3. **Convertir** el JSON a un objeto Python tipado

**Archivo:** `models/producto.py`

```python
"""Modelo Pydantic para la tabla producto."""
# ↑ Docstring del módulo. Este archivo define el modelo de validación
# para la entidad producto. Pydantic v2 lo usa para validar los datos
# que llegan en el body de las peticiones POST y PUT.

from pydantic import BaseModel
# ↑ BaseModel es la clase base de Pydantic para modelos de datos.
# Toda clase que herede de BaseModel obtiene:
# - Validación automática de tipos al crear una instancia
# - Método model_dump() para convertir a diccionario
# - Serialización JSON automática
# - Documentación automática en Swagger UI


class Producto(BaseModel):
    """Representa un producto en la base de datos."""
    # ↑ Hereda de BaseModel → obtiene todas las capacidades de Pydantic.
    # Esta clase define 4 campos que corresponden a las 4 columnas
    # de la tabla producto en PostgreSQL.

    codigo: str
    # ↑ Campo obligatorio, tipo string.
    # Corresponde a: producto.codigo VARCHAR(30) NOT NULL
    # Si el cliente no envía "codigo" o envía un número,
    # Pydantic rechaza con error 422.
    # Pydantic convierte automáticamente: 123 → "123" (coerción a str).

    nombre: str
    # ↑ Campo obligatorio, tipo string.
    # Corresponde a: producto.nombre VARCHAR(100) NOT NULL

    stock: int | None = None
    # ↑ Campo OPCIONAL, tipo entero o None.
    # int | None → acepta un entero o None (equivale a Optional[int]).
    # = None → valor por defecto si no se envía.
    # Corresponde a: producto.stock INTEGER NOT NULL
    #
    # ¿Por qué es opcional en el modelo si es NOT NULL en la BD?
    # Porque en un UPDATE puedes querer cambiar solo el nombre,
    # sin enviar stock. El servicio y repositorio manejan qué campos
    # incluir en el SQL.
    #
    # Validación: si envían "abc", Pydantic rechaza con 422.
    # Coerción: si envían "20" (string), Pydantic convierte a int 20.

    valorunitario: float | None = None
    # ↑ Campo OPCIONAL, tipo decimal o None.
    # float | None → acepta un número decimal o None.
    # Corresponde a: producto.valorunitario NUMERIC(14,2) NOT NULL
    #
    # Nota: usamos float en el modelo (no Decimal) porque JSON no tiene
    # tipo Decimal. El repositorio se encarga de la conversión precisa
    # cuando interactúa con PostgreSQL.
```

### ¿Qué pasa cuando el cliente envía datos?

| JSON del cliente | ¿Pydantic acepta? | Resultado |
|-----------------|-------------------|-----------|
| `{"codigo": "PR006", "nombre": "Mouse", "stock": 10, "valorunitario": 50000}` | Si | Objeto Producto válido |
| `{"codigo": "PR006", "nombre": "Mouse"}` | Si | stock=None, valorunitario=None |
| `{"nombre": "Mouse", "stock": 10}` | **No** | Error 422: falta "codigo" (obligatorio) |
| `{"codigo": "PR006", "nombre": "Mouse", "stock": "abc"}` | **No** | Error 422: stock debe ser entero |
| `{"codigo": 123, "nombre": "Mouse"}` | Si | codigo="123" (coerción automática) |

### Método `model_dump()`:

```python
producto = Producto(codigo="PR006", nombre="Mouse", stock=10, valorunitario=50000)
datos = producto.model_dump()
# datos = {"codigo": "PR006", "nombre": "Mouse", "stock": 10, "valorunitario": 50000.0}

# Con exclude para el UPDATE (no enviar el código en el SET):
datos_sin_pk = producto.model_dump(exclude={"codigo"})
# datos_sin_pk = {"nombre": "Mouse", "stock": 10, "valorunitario": 50000.0}
```

### `models/__init__.py`

```python
"""Paquete de modelos Pydantic."""

from .producto import Producto
# ↑ Exporta Producto para importar como:
#   from models.producto import Producto
#   o: from models import Producto
```

---

## 5.3 `producto_controller.py` — Los 5 endpoints HTTP

Este archivo es el **punto de entrada HTTP**. Define las rutas (URLs) que el cliente puede llamar y conecta cada petición con el servicio correspondiente.

**Archivo:** `controllers/producto_controller.py`

### 5.3.1 Imports y configuración del router

```python
"""
producto_controller.py — Controller específico para la tabla producto.

Endpoints:
- GET    /api/producto/              → Listar productos
- GET    /api/producto/{codigo}      → Obtener producto por código
- POST   /api/producto/              → Crear producto
- PUT    /api/producto/{codigo}      → Actualizar producto
- DELETE /api/producto/{codigo}      → Eliminar producto
"""
# ↑ Docstring del módulo. Lista los 5 endpoints que este controller expone.
# Cada endpoint corresponde a una operación CRUD:
#   C = Create (POST)
#   R = Read (GET)
#   U = Update (PUT)
#   D = Delete (DELETE)

from fastapi import APIRouter, HTTPException, Query, Response
# ↑ Imports de FastAPI:
# APIRouter: crea un grupo de rutas con un prefijo común.
#   Es como un "mini app" que se registra en el app principal.
# HTTPException: lanza errores HTTP con código de estado y detalle.
#   Ejemplo: HTTPException(status_code=404, detail="No encontrado")
# Query: define parámetros de query string (?esquema=public&limite=10).
#   Permite documentar y validar parámetros de URL.
# Response: permite retornar respuestas HTTP personalizadas.
#   Lo usamos para retornar 204 No Content (sin body).

from models.producto import Producto
# ↑ Importa el modelo Pydantic. FastAPI lo usa para:
# 1. Validar el body de POST y PUT automáticamente
# 2. Generar la documentación en Swagger UI

from servicios.fabrica_repositorios import crear_servicio_producto
# ↑ Importa la fábrica. El controller NUNCA crea repositorios ni
# servicios directamente — siempre usa la fábrica.
# Esto mantiene al controller desacoplado de la implementación.


router = APIRouter(prefix="/api/producto", tags=["Producto"])
# ↑ Crea el router con:
# prefix="/api/producto" → todas las rutas empiezan con /api/producto
#   @router.get("/") → GET /api/producto/
#   @router.get("/{codigo}") → GET /api/producto/PR001
# tags=["Producto"] → agrupa estos endpoints bajo "Producto" en Swagger UI.
#   Swagger UI muestra los endpoints organizados por tags.
```

### 5.3.2 GET / — Listar todos los productos

```python
# =========================================================================
# GET /api/producto/ — Listar todos los productos
# =========================================================================

@router.get("/")
# ↑ Decorador que registra esta función como handler del GET /api/producto/
# Cuando el cliente hace GET /api/producto/, FastAPI llama a esta función.
async def listar_productos(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todos los productos."""
    # ↑ Parámetros de query string (van en la URL después del ?):
    #   GET /api/producto/?esquema=public&limite=10
    # Query(default=None) → el parámetro es opcional, default None.
    # FastAPI los documenta automáticamente en Swagger UI.
    # Si el cliente no los envía, ambos son None.
    try:
        servicio = crear_servicio_producto()
        # ↑ La fábrica crea el servicio completo:
        # ProveedorConexion → RepositorioProductoPostgreSQL → ServicioProducto
        # El controller no sabe qué BD se usa.

        filas = await servicio.listar(esquema, limite)
        # ↑ await → espera el resultado sin bloquear.
        # servicio.listar() → normaliza parámetros → repo.obtener_todos() → SQL
        # Retorna: [{"codigo": "PR001", "nombre": "Laptop", ...}, ...]

        if len(filas) == 0:
            return Response(status_code=204)
        # ↑ Si no hay productos, retorna 204 No Content (sin body).
        # 204 significa "la petición fue exitosa pero no hay contenido que devolver".
        # Es más correcto que retornar 200 con una lista vacía [].

        return {
            "tabla": "producto",
            "total": len(filas),
            "datos": filas
        }
        # ↑ Retorna un diccionario que FastAPI convierte a JSON automáticamente.
        # Ejemplo de respuesta:
        # {
        #   "tabla": "producto",
        #   "total": 5,
        #   "datos": [
        #     {"codigo": "PR001", "nombre": "Laptop Lenovo", "stock": 20, "valorunitario": 2500000.0},
        #     {"codigo": "PR002", "nombre": "Monitor Samsung", "stock": 30, "valorunitario": 800000.0},
        #     ...
        #   ]
        # }

    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": str(ex)
        })
    # ↑ ValueError viene del servicio (validaciones de negocio).
    # 400 Bad Request = "los datos que enviaste son incorrectos".

    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
    # ↑ Cualquier otro error (conexión BD, SQL, etc.).
    # 500 Internal Server Error = "algo salió mal en el servidor".
    # str(ex) incluye el mensaje del error para facilitar el debug.
```

### 5.3.3 GET /{codigo} — Obtener producto por código

```python
# =========================================================================
# GET /api/producto/{codigo} — Obtener producto por código
# =========================================================================

@router.get("/{codigo}")
# ↑ {codigo} es un PATH PARAMETER: va en la URL, no en query string.
#   GET /api/producto/PR001 → codigo = "PR001"
# FastAPI extrae el valor automáticamente y lo pasa al parámetro 'codigo'.
async def obtener_producto(
    codigo: str,
    esquema: str | None = Query(default=None)
):
    """Obtiene un producto por su código."""
    # ↑ codigo: str → viene de la URL (path parameter).
    # esquema → viene del query string (opcional).
    try:
        servicio = crear_servicio_producto()
        filas = await servicio.obtener_por_codigo(codigo, esquema)
        # ↑ Busca el producto por su PK.
        # Si PR001 existe: [{"codigo": "PR001", ...}]
        # Si no existe: []

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontró producto con codigo = {codigo}"
            })
        # ↑ Si no encontró el producto, retorna 404 Not Found.
        # 404 = "el recurso que buscas no existe".
        # f"..." → f-string: inserta el valor de 'codigo' en el mensaje.

        return {
            "tabla": "producto",
            "total": len(filas),
            "datos": filas
        }

    except HTTPException:
        raise
    # ↑ IMPORTANTE: re-lanza las HTTPException que ya creamos arriba (404).
    # Sin este bloque, el except Exception las capturaría y las convertiría
    # en un 500, perdiendo el código 404 original.
    # "raise" sin argumentos re-lanza la misma excepción.

    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
```

### 5.3.4 POST / — Crear producto

```python
# =========================================================================
# POST /api/producto/ — Crear producto
# =========================================================================

@router.post("/")
async def crear_producto(
    producto: Producto,
    esquema: str | None = Query(default=None)
):
    """Crea un nuevo producto. Valida con el modelo Pydantic."""
    # ↑ producto: Producto → FastAPI espera un JSON en el body de la petición.
    # Pydantic lo valida automáticamente contra el modelo Producto:
    #   - ¿Tiene "codigo" (str)? ¿Tiene "nombre" (str)?
    #   - ¿"stock" es int o None? ¿"valorunitario" es float o None?
    # Si el JSON es inválido, FastAPI retorna 422 SIN ejecutar esta función.
    #
    # esquema → query string opcional (para seleccionar esquema de BD).
    try:
        datos = producto.model_dump()
        # ↑ Convierte el objeto Pydantic a diccionario Python.
        # Producto(codigo="PR006", nombre="Mouse", stock=10, valorunitario=50000)
        # → {"codigo": "PR006", "nombre": "Mouse", "stock": 10, "valorunitario": 50000.0}

        servicio = crear_servicio_producto()
        creado = await servicio.crear(datos, esquema)
        # ↑ El servicio valida que datos no esté vacío,
        # normaliza el esquema y delega al repositorio.
        # El repositorio ejecuta el INSERT.

        if creado:
            return {
                "estado": 200,
                "mensaje": "Producto creado exitosamente.",
                "datos": datos
            }
        # ↑ Si el INSERT afectó al menos 1 fila, retorna éxito.
        # Incluye los datos creados para que el cliente los confirme.
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear el producto."
            })
        # ↑ Si el INSERT no afectó filas (raro pero posible).

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
```

### 5.3.5 PUT /{codigo} — Actualizar producto

```python
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
    # ↑ codigo: str → viene de la URL: PUT /api/producto/PR001
    # producto: Producto → viene del body (JSON validado por Pydantic).
    # esquema → query string opcional.
    try:
        datos = producto.model_dump(exclude={"codigo"})
        # ↑ IMPORTANTE: exclude={"codigo"} excluye el campo "codigo" del diccionario.
        # ¿Por qué? Porque el código ya viene en la URL (path parameter).
        # No queremos que el UPDATE intente cambiar la PK.
        # Resultado: {"nombre": "Laptop Gamer", "stock": 15, "valorunitario": 3000000.0}

        servicio = crear_servicio_producto()
        filas = await servicio.actualizar(codigo, datos, esquema)
        # ↑ servicio.actualizar() valida que codigo y datos no estén vacíos.
        # repo.actualizar() ejecuta: UPDATE producto SET ... WHERE codigo = 'PR001'
        # Retorna: número de filas afectadas (0 o 1).

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
        # ↑ Si filas == 0, el producto no existe → 404.

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
```

### 5.3.6 DELETE /{codigo} — Eliminar producto

```python
# =========================================================================
# DELETE /api/producto/{codigo} — Eliminar producto
# =========================================================================

@router.delete("/{codigo}")
async def eliminar_producto(
    codigo: str,
    esquema: str | None = Query(default=None)
):
    """Elimina un producto por su código."""
    # ↑ codigo → de la URL: DELETE /api/producto/PR001
    # No hay body — DELETE no necesita datos, solo el identificador.
    try:
        servicio = crear_servicio_producto()
        filas = await servicio.eliminar(codigo, esquema)
        # ↑ repo.eliminar() ejecuta: DELETE FROM producto WHERE codigo = 'PR001'
        # Retorna: filas eliminadas (0 o 1).

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
```

---

## 5.4 Códigos de estado HTTP usados

| Código | Nombre | Cuándo se usa en este controller |
|--------|--------|--------------------------------|
| **200** | OK | GET con datos, POST exitoso, PUT exitoso, DELETE exitoso |
| **204** | No Content | GET listar cuando no hay productos |
| **400** | Bad Request | ValueError del servicio (datos inválidos) |
| **404** | Not Found | GET/PUT/DELETE cuando el código no existe |
| **422** | Unprocessable Entity | Pydantic rechaza el JSON (tipo incorrecto) |
| **500** | Internal Server Error | Error de BD, conexión, o cualquier excepción no esperada |

---

## 5.5 Estructura de manejo de errores

Todos los endpoints siguen el mismo patrón de try/except:

```python
try:
    # 1. Crear servicio con la fábrica
    # 2. Ejecutar la operación
    # 3. Retornar resultado o lanzar 404

except HTTPException:
    raise                    # ← Re-lanza 404 (no la conviertas en 500)

except ValueError as ex:
    raise HTTPException(400) # ← Error de validación del servicio

except Exception as ex:
    raise HTTPException(500) # ← Cualquier otro error (BD, conexión, etc.)
```

**¿Por qué `except HTTPException: raise`?** Sin este bloque, si lanzas un HTTPException(404) dentro del try, el `except Exception` lo capturaría y lo convertiría en un 500. El `except HTTPException: raise` lo deja pasar sin modificarlo.

---

## Resumen de la Parte 5

### Archivos creados

| # | Archivo | Capa | Líneas | Propósito |
|---|---------|------|--------|-----------|
| 1 | `models/producto.py` | Modelo | 12 | Validación Pydantic: 4 campos (codigo, nombre, stock, valorunitario) |
| 2 | `models/__init__.py` | Config | 3 | Export de Producto |
| 3 | `controllers/producto_controller.py` | Presentación | ~200 | 5 endpoints HTTP (GET, GET/{id}, POST, PUT, DELETE) |

### Los 5 endpoints

| Método | Ruta | Body | Retorna | Código éxito | Código error |
|--------|------|------|---------|-------------|-------------|
| GET | `/api/producto/` | — | Lista de productos | 200 / 204 | 500 |
| GET | `/api/producto/{codigo}` | — | Un producto | 200 | 404 / 500 |
| POST | `/api/producto/` | JSON Producto | Confirmación | 200 | 400 / 422 / 500 |
| PUT | `/api/producto/{codigo}` | JSON Producto | Filas afectadas | 200 | 400 / 404 / 422 / 500 |
| DELETE | `/api/producto/{codigo}` | — | Filas eliminadas | 200 | 404 / 500 |

### Flujo de una petición POST

```
Cliente HTTP (Postman/Swagger)
  │  POST /api/producto/
  │  Body: {"codigo": "PR006", "nombre": "Mouse", "stock": 10, "valorunitario": 50000}
  │
  ▼
FastAPI + Pydantic
  │  1. Valida JSON contra modelo Producto ← Si falla: 422
  │  2. Crea objeto Producto(codigo="PR006", ...)
  │
  ▼
producto_controller.py → crear_producto()
  │  3. producto.model_dump() → dict
  │  4. crear_servicio_producto() → ServicioProducto
  │  5. await servicio.crear(datos)
  │
  ▼
servicio_producto.py → crear()
  │  6. Valida que datos no esté vacío
  │  7. Normaliza esquema
  │  8. await self._repo.crear(datos)
  │
  ▼
repositorio_producto_postgresql.py → crear()
  │  9. await self._crear("producto", datos)
  │
  ▼
base_repositorio_postgresql.py → _crear()
  │  10. Detecta tipos de columnas
  │  11. Convierte valores (str→int, str→Decimal)
  │  12. INSERT INTO "public"."producto" (...) VALUES (...)
  │
  ▼
PostgreSQL → INSERT ejecutado → rowcount = 1

  ▲ Respuesta sube por todas las capas
  │
  200 OK: {"estado": 200, "mensaje": "Producto creado exitosamente.", "datos": {...}}
```

---

## Siguiente paso

En la **Parte 6** crearemos el **`main.py`** (punto de entrada de la aplicación), ejecutaremos la API con `uvicorn` y probaremos los 5 endpoints con Swagger UI.

---

> **Nota:** Al terminar esta parte, ya tienes TODAS las capas de código completas. Solo falta el `main.py` para conectar el router con la aplicación FastAPI y poder ejecutar.
