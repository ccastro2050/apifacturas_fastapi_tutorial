# PARTE 6 — Punto de Entrada: `main.py` y Ejecucion

> En esta parte creamos el **archivo final** del proyecto: `main.py`. Este archivo conecta todo lo que construimos en las partes anteriores (repositorio, servicio, controller) y arranca la aplicacion con `uvicorn`. Tambien probaremos los 5 endpoints desde Swagger UI.

> **Nota:** Si ya sabes como funciona `main.py` en FastAPI, puedes ir directamente al **Resumen** al final de esta parte.

---

## 6.1 `main.py` — Punto de entrada de la aplicacion

El archivo `main.py` es el **punto de entrada** de toda aplicacion FastAPI. Su trabajo es simple:

1. Crear la instancia de la aplicacion FastAPI
2. Registrar los routers (controllers)
3. Definir un endpoint raiz de verificacion

En el proyecto original completo, `main.py` registra 13 routers (persona, empresa, cliente, vendedor, producto, factura, etc.). Para este tutorial, **solo registramos el router de producto**.

### Comparacion: proyecto original vs tutorial

| | Proyecto original | Tutorial |
|---|---|---|
| **Routers** | 13 (persona, empresa, cliente, vendedor, producto, factura, detalle, usuario, rol, rol_usuario, ruta, rutarol, entidades) | 1 (producto) |
| **Imports** | 13 lineas de import | 1 linea de import |
| **include_router()** | 13 llamadas | 1 llamada |
| **Lineas totales** | ~50 | ~25 |

### Codigo completo: `main.py`

**Archivo:** `main.py` (raiz del proyecto)

```python
"""
main.py — Punto de entrada de la API REST con FastAPI.
"""
# ↑ Docstring del modulo. Describe el proposito de este archivo.
# Este es el unico archivo que se ejecuta directamente.
# Todos los demas (controllers, servicios, repositorios) son importados.

# ── Importaciones ─────────────────────────────────────────────────────

from fastapi import FastAPI
# ↑ FastAPI: clase principal del framework.
# Crear una instancia de FastAPI() es crear la aplicacion web completa.
# Esta instancia es el punto central que:
# - Recibe todas las peticiones HTTP
# - Las enruta al controller correcto
# - Genera la documentacion automatica (Swagger UI y ReDoc)

from controllers.producto_controller import router as producto_router
# ↑ Importa el router del controller de productos.
# "router" es el APIRouter definido en producto_controller.py (Parte 5).
# "as producto_router" le da un alias descriptivo.
# Este router contiene los 5 endpoints: GET, GET/{codigo}, POST, PUT, DELETE.

# ── Crear instancia de la aplicacion ──────────────────────────────────

app = FastAPI(
    title="API Producto - Tutorial FastAPI",
    # ↑ Titulo que aparece en Swagger UI (/docs) y ReDoc (/redoc).

    description="API REST CRUD para la tabla producto — Tutorial.",
    # ↑ Descripcion que aparece debajo del titulo en la documentacion.

    version="1.0.0",
    # ↑ Version de la API. Aparece junto al titulo en /docs.
)
# ↑ app es LA aplicacion. Todo pasa a traves de este objeto.
# uvicorn busca este objeto por nombre: uvicorn main:app
#                                               ↑      ↑
#                                           archivo  variable

# ── Registrar el controller ──────────────────────────────────────────

app.include_router(producto_router)
# ↑ Conecta el router de productos a la aplicacion.
# Esto le dice a FastAPI: "todas las rutas definidas en producto_router
# ahora son parte de esta aplicacion".
# Sin esta linea, los endpoints de producto NO existirian.
# Despues de esto, la API tiene 5 endpoints activos:
#   GET    /api/producto/
#   GET    /api/producto/{codigo}
#   POST   /api/producto/
#   PUT    /api/producto/{codigo}
#   DELETE /api/producto/{codigo}

# ── Endpoint raiz ────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
# ↑ Decora la funcion como handler de GET /
# tags=["Root"] → la agrupa bajo la etiqueta "Root" en Swagger UI.
async def root():
    """Endpoint raiz de verificacion."""
    # ↑ Sirve para comprobar rapidamente que la API esta activa.
    # Es una convencion comun en APIs REST.
    return {
        "mensaje": "API Producto - Tutorial FastAPI activa.",
        # ↑ Mensaje de confirmacion.
        "docs": "/docs",
        # ↑ URL de Swagger UI (documentacion interactiva).
        "redoc": "/redoc"
        # ↑ URL de ReDoc (documentacion alternativa, solo lectura).
    }
    # ↑ FastAPI convierte este diccionario a JSON automaticamente.
    # El cliente recibe: {"mensaje": "...", "docs": "/docs", "redoc": "/redoc"}
```

### Diagrama de flujo: que hace `main.py`

```
main.py
  │
  ├── 1. Importa FastAPI
  │
  ├── 2. Importa producto_router (del controller)
  │
  ├── 3. Crea app = FastAPI(title=..., description=..., version=...)
  │
  ├── 4. Registra: app.include_router(producto_router)
  │       → Ahora la app tiene 5 endpoints de producto
  │
  └── 5. Define endpoint raiz: GET / → {"mensaje": "API activa..."}

uvicorn main:app --reload
  │
  └── uvicorn encuentra app en main.py y arranca el servidor HTTP
```

### ¿Que es `include_router()` y por que se necesita?

`include_router()` es el metodo que **conecta** un router a la aplicacion principal. Sin el, los endpoints definidos en el controller no existirian.

```python
# Sin include_router: la app solo tiene GET /
app = FastAPI()

# Con include_router: la app tiene GET / + 5 endpoints de producto
app.include_router(producto_router)
```

**Analogia:** `FastAPI()` es un edificio vacio. `include_router()` instala un departamento con sus habitaciones (endpoints). Si necesitas mas departamentos (clientes, facturas, etc.), llamas a `include_router()` una vez por cada router.

---

## 6.2 Ejecutar la API

### Prerrequisitos antes de ejecutar

Antes de arrancar la API, verifica:

| # | Requisito | Como verificar |
|---|-----------|---------------|
| 1 | **Entorno virtual activo** | El prompt muestra `(venv)` al inicio |
| 2 | **Dependencias instaladas** | `pip list` muestra fastapi, uvicorn, sqlalchemy, asyncpg, etc. |
| 3 | **PostgreSQL corriendo** | El servicio de PostgreSQL esta activo |
| 4 | **Base de datos creada** | La base de datos y la tabla `producto` existen con datos |
| 5 | **`.env` configurado** | El archivo `.env` tiene la cadena de conexion correcta |

### Activar el entorno virtual

```bash
# Windows (CMD)
venv\Scripts\activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate
```

Despues de activar, el prompt cambia a:

```
(venv) C:\ruta\al\proyecto>
```

### Comando para ejecutar

```bash
uvicorn main:app --reload
```

### ¿Que significa cada parte del comando?

| Parte | Significado |
|-------|-------------|
| `uvicorn` | Servidor ASGI (Asynchronous Server Gateway Interface). Es el "motor" que ejecuta aplicaciones FastAPI. |
| `main` | Nombre del archivo Python: `main.py` (sin la extension `.py`). |
| `:` | Separador entre archivo y variable. |
| `app` | Nombre de la variable `FastAPI()` dentro de `main.py`. |
| `--reload` | Reinicia automaticamente el servidor cuando detecta cambios en el codigo. **Solo para desarrollo.** |

### Parametros opcionales de uvicorn

| Parametro | Default | Ejemplo | Descripcion |
|-----------|---------|---------|-------------|
| `--host` | `127.0.0.1` | `--host 0.0.0.0` | IP donde escucha. `0.0.0.0` = accesible desde otras maquinas en la red. |
| `--port` | `8000` | `--port 3000` | Puerto donde escucha. Cambiar si 8000 esta ocupado. |
| `--reload` | desactivado | `--reload` | Reinicio automatico al detectar cambios. Solo para desarrollo. |
| `--workers` | `1` | `--workers 4` | Numero de procesos. Para produccion (no compatible con `--reload`). |

### Ejemplos de ejecucion con diferentes parametros

```bash
# Basico (desarrollo) — lo mas comun
uvicorn main:app --reload

# Cambiar puerto (si 8000 esta ocupado)
uvicorn main:app --reload --port 3000

# Accesible desde otras maquinas en la red local
uvicorn main:app --reload --host 0.0.0.0

# Produccion (sin --reload, con multiples workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Salida esperada en la terminal

Cuando ejecutas `uvicorn main:app --reload`, la terminal muestra:

```
INFO:     Will watch for changes in these directories: ['C:\\ruta\\al\\proyecto']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

| Linea | Significado |
|-------|-------------|
| `Will watch for changes` | `--reload` activo: vigila cambios en archivos `.py` |
| `running on http://127.0.0.1:8000` | La API esta escuchando en localhost puerto 8000 |
| `Press CTRL+C to quit` | Para detener el servidor, presiona Ctrl+C |
| `Started reloader process` | Proceso que vigila cambios en archivos |
| `Started server process` | Proceso que atiende peticiones HTTP |
| `Application startup complete` | La API esta lista para recibir peticiones |

### URLs disponibles despues de ejecutar

| URL | Descripcion |
|-----|-------------|
| `http://127.0.0.1:8000/` | Endpoint raiz: verifica que la API esta activa |
| `http://127.0.0.1:8000/docs` | **Swagger UI**: documentacion interactiva. Permite probar endpoints directamente desde el navegador. |
| `http://127.0.0.1:8000/redoc` | **ReDoc**: documentacion alternativa. Solo lectura, formato mas limpio para consulta. |
| `http://127.0.0.1:8000/api/producto/` | Endpoint de productos (GET listar) |

### Swagger UI (`/docs`)

Al abrir `http://127.0.0.1:8000/docs` en el navegador, veras la interfaz Swagger UI con:

- El titulo **"API Producto - Tutorial FastAPI"** en la parte superior
- La version **1.0.0** junto al titulo
- Dos grupos de endpoints:
  - **Producto** (5 endpoints): GET, GET/{codigo}, POST, PUT, DELETE
  - **Root** (1 endpoint): GET /
- Cada endpoint tiene un boton **"Try it out"** para probarlo directamente

### ReDoc (`/redoc`)

Al abrir `http://127.0.0.1:8000/redoc` en el navegador, veras la documentacion en formato ReDoc:

- La misma informacion que Swagger UI pero en formato de solo lectura
- Mejor organizado para documentacion de referencia
- No permite probar endpoints (solo verlos)

### Verificar que la API esta activa

Abre el navegador y navega a `http://127.0.0.1:8000/`. Deberias ver:

```json
{
    "mensaje": "API Producto - Tutorial FastAPI activa.",
    "docs": "/docs",
    "redoc": "/redoc"
}
```

Si ves este JSON, la API esta corriendo correctamente.

---

## 6.3 Probar con Swagger UI

Vamos a probar los **5 endpoints** del CRUD completo usando Swagger UI. Abre `http://127.0.0.1:8000/docs` en el navegador.

La base de datos ya tiene 5 productos de ejemplo (PR001 a PR005). Vamos a:

1. **Crear** un producto nuevo (PR999)
2. **Listar** todos los productos (verificar que PR999 aparece)
3. **Obtener** el producto PR999 por codigo
4. **Actualizar** el producto PR999
5. **Eliminar** el producto PR999

### Paso 1: POST — Crear producto PR999

**Endpoint:** `POST /api/producto/`

**Instrucciones en Swagger UI:**
1. Haz clic en el endpoint **POST /api/producto/**
2. Haz clic en el boton **"Try it out"**
3. En el campo **"Request body"**, reemplaza el JSON de ejemplo con el siguiente:

**Request body (JSON):**

```json
{
    "codigo": "PR999",
    "nombre": "Producto Tutorial",
    "stock": 50,
    "valorunitario": 25000.0
}
```

4. Haz clic en el boton **"Execute"**

**Respuesta esperada (HTTP 200):**

```json
{
    "estado": 200,
    "mensaje": "Producto creado exitosamente.",
    "datos": {
        "codigo": "PR999",
        "nombre": "Producto Tutorial",
        "stock": 50,
        "valorunitario": 25000.0
    }
}
```

**¿Que paso internamente?**

```
Swagger UI → POST /api/producto/ con body JSON
  → FastAPI valida el JSON con el modelo Pydantic Producto
  → producto_controller.py → crear_producto()
  → servicio_producto.py → crear()
  → repositorio_producto_postgresql.py → crear()
  → base_repositorio_postgresql.py → _crear()
  → PostgreSQL: INSERT INTO "public"."producto" (codigo, nombre, stock, valorunitario)
                VALUES ('PR999', 'Producto Tutorial', 50, 25000.0)
  → Respuesta: 200 OK + JSON de confirmacion
```

**Si envias datos invalidos:**

```json
{
    "codigo": "PR999",
    "nombre": "Producto Tutorial",
    "stock": "no-es-numero",
    "valorunitario": 25000.0
}
```

FastAPI/Pydantic rechaza la peticion **antes** de ejecutar tu codigo:

```json
{
    "detail": [
        {
            "type": "int_parsing",
            "loc": ["body", "stock"],
            "msg": "Input should be a valid integer, unable to parse string as an integer",
            "input": "no-es-numero"
        }
    ]
}
```

**Codigo HTTP:** 422 Unprocessable Entity.

---

### Paso 2: GET — Listar todos los productos

**Endpoint:** `GET /api/producto/`

**Instrucciones en Swagger UI:**
1. Haz clic en el endpoint **GET /api/producto/**
2. Haz clic en **"Try it out"**
3. Deja los parametros `esquema` y `limite` vacios (opcional)
4. Haz clic en **"Execute"**

**Respuesta esperada (HTTP 200):**

```json
{
    "tabla": "producto",
    "total": 6,
    "datos": [
        {
            "codigo": "PR001",
            "nombre": "Laptop HP Pavilion",
            "stock": 10,
            "valorunitario": 2500000.00
        },
        {
            "codigo": "PR002",
            "nombre": "Mouse Logitech M185",
            "stock": 50,
            "valorunitario": 45000.00
        },
        {
            "codigo": "PR003",
            "nombre": "Teclado Mecanico Redragon",
            "stock": 30,
            "valorunitario": 120000.00
        },
        {
            "codigo": "PR004",
            "nombre": "Monitor Samsung 24 pulgadas",
            "stock": 15,
            "valorunitario": 650000.00
        },
        {
            "codigo": "PR005",
            "nombre": "Audifonos Sony WH-1000XM5",
            "stock": 20,
            "valorunitario": 900000.00
        },
        {
            "codigo": "PR999",
            "nombre": "Producto Tutorial",
            "stock": 50,
            "valorunitario": 25000.00
        }
    ]
}
```

**Nota:** El `"total": 6` confirma que ahora hay 6 productos (los 5 originales + PR999 que acabamos de crear).

**Probando con el parametro `limite`:**

Si ingresas `limite = 2` en Swagger UI, la respuesta solo muestra los primeros 2 productos:

```json
{
    "tabla": "producto",
    "total": 2,
    "datos": [
        {
            "codigo": "PR001",
            "nombre": "Laptop HP Pavilion",
            "stock": 10,
            "valorunitario": 2500000.00
        },
        {
            "codigo": "PR002",
            "nombre": "Mouse Logitech M185",
            "stock": 50,
            "valorunitario": 45000.00
        }
    ]
}
```

---

### Paso 3: GET /{codigo} — Obtener producto PR999

**Endpoint:** `GET /api/producto/{codigo}`

**Instrucciones en Swagger UI:**
1. Haz clic en el endpoint **GET /api/producto/{codigo}**
2. Haz clic en **"Try it out"**
3. En el campo **"codigo"**, escribe: `PR999`
4. Haz clic en **"Execute"**

**Respuesta esperada (HTTP 200):**

```json
{
    "tabla": "producto",
    "total": 1,
    "datos": [
        {
            "codigo": "PR999",
            "nombre": "Producto Tutorial",
            "stock": 50,
            "valorunitario": 25000.00
        }
    ]
}
```

**Si buscas un producto que no existe (ejemplo: PR000):**

```json
{
    "detail": {
        "estado": 404,
        "mensaje": "No se encontro producto con codigo = PR000"
    }
}
```

**Codigo HTTP:** 404 Not Found.

---

### Paso 4: PUT /{codigo} — Actualizar producto PR999

**Endpoint:** `PUT /api/producto/{codigo}`

**Instrucciones en Swagger UI:**
1. Haz clic en el endpoint **PUT /api/producto/{codigo}**
2. Haz clic en **"Try it out"**
3. En el campo **"codigo"**, escribe: `PR999`
4. En el campo **"Request body"**, ingresa:

**Request body (JSON):**

```json
{
    "codigo": "PR999",
    "nombre": "Producto Actualizado",
    "stock": 100,
    "valorunitario": 25000.0
}
```

> **Nota:** El campo `"codigo"` en el body es requerido por el modelo Pydantic (es `str`, no `str | None`), pero el controller lo excluye con `model_dump(exclude={"codigo"})` antes de ejecutar el UPDATE. El codigo que se usa para el WHERE viene de la URL, no del body.

5. Haz clic en **"Execute"**

**Respuesta esperada (HTTP 200):**

```json
{
    "estado": 200,
    "mensaje": "Producto actualizado exitosamente.",
    "filtro": "codigo = PR999",
    "filasAfectadas": 1
}
```

**Verificar la actualizacion:**

Repite el Paso 3 (GET /api/producto/PR999) para confirmar que los datos cambiaron:

```json
{
    "tabla": "producto",
    "total": 1,
    "datos": [
        {
            "codigo": "PR999",
            "nombre": "Producto Actualizado",
            "stock": 100,
            "valorunitario": 25000.00
        }
    ]
}
```

El nombre cambio de "Producto Tutorial" a **"Producto Actualizado"** y el stock cambio de 50 a **100**.

---

### Paso 5: DELETE /{codigo} — Eliminar producto PR999

**Endpoint:** `DELETE /api/producto/{codigo}`

**Instrucciones en Swagger UI:**
1. Haz clic en el endpoint **DELETE /api/producto/{codigo}**
2. Haz clic en **"Try it out"**
3. En el campo **"codigo"**, escribe: `PR999`
4. Haz clic en **"Execute"**

**Respuesta esperada (HTTP 200):**

```json
{
    "estado": 200,
    "mensaje": "Producto eliminado exitosamente.",
    "filtro": "codigo = PR999",
    "filasEliminadas": 1
}
```

**Verificar la eliminacion:**

Repite el Paso 3 (GET /api/producto/PR999). Ahora deberias recibir:

```json
{
    "detail": {
        "estado": 404,
        "mensaje": "No se encontro producto con codigo = PR999"
    }
}
```

**Codigo HTTP:** 404 Not Found. El producto PR999 ya no existe.

**Si intentas eliminar de nuevo PR999:**

```json
{
    "detail": {
        "estado": 404,
        "mensaje": "No existe producto con codigo = PR999"
    }
}
```

**Codigo HTTP:** 404 Not Found. No puedes eliminar algo que no existe.

---

### Resumen de las pruebas

| # | Operacion | Endpoint | Codigo HTTP | Resultado |
|---|-----------|----------|-------------|-----------|
| 1 | Crear PR999 | POST /api/producto/ | 200 | Producto creado exitosamente |
| 2 | Listar todos | GET /api/producto/ | 200 | 6 productos (incluyendo PR999) |
| 3 | Obtener PR999 | GET /api/producto/PR999 | 200 | Datos del producto PR999 |
| 4 | Actualizar PR999 | PUT /api/producto/PR999 | 200 | Nombre y stock actualizados |
| 5 | Eliminar PR999 | DELETE /api/producto/PR999 | 200 | Producto eliminado |
| 6 | Verificar eliminacion | GET /api/producto/PR999 | 404 | Producto no encontrado |

---

## 6.4 Errores comunes al ejecutar

### Error 1: `ModuleNotFoundError: No module named 'fastapi'`

```
ModuleNotFoundError: No module named 'fastapi'
```

**Causa:** El entorno virtual no esta activo o las dependencias no estan instaladas.

**Solucion:**
```bash
# 1. Activar el entorno virtual
venv\Scripts\activate          # Windows CMD
.\venv\Scripts\Activate.ps1    # Windows PowerShell
source venv/bin/activate       # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt
```

---

### Error 2: `ModuleNotFoundError: No module named 'controllers'`

```
ModuleNotFoundError: No module named 'controllers'
```

**Causa:** Estas ejecutando uvicorn desde un directorio diferente al del proyecto.

**Solucion:** Navega al directorio raiz del proyecto antes de ejecutar:

```bash
cd C:\ruta\al\apifacturas_fastapi_tutorial
uvicorn main:app --reload
```

`main.py` debe estar en el mismo directorio desde donde ejecutas el comando.

---

### Error 3: `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`

```
ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000):
          only one usage of each socket address is normally permitted
```

**Causa:** El puerto 8000 ya esta en uso (otra instancia de uvicorn, u otra aplicacion).

**Solucion (opcion A):** Detener el proceso que ocupa el puerto:
```bash
# Windows: buscar el proceso que usa el puerto 8000
netstat -ano | findstr :8000

# Terminar el proceso (reemplaza PID con el numero que aparece)
taskkill /PID <PID> /F
```

**Solucion (opcion B):** Usar un puerto diferente:
```bash
uvicorn main:app --reload --port 3000
```

---

### Error 4: `Connection refused` o error de conexion a PostgreSQL

```
asyncpg.exceptions.ConnectionDoesNotExistError: connection was closed
```

o

```
sqlalchemy.exc.OperationalError: (asyncpg.exceptions...)
```

**Causa:** PostgreSQL no esta corriendo o la cadena de conexion en `.env` es incorrecta.

**Solucion:**
1. Verificar que el servicio de PostgreSQL este activo
2. Verificar el archivo `.env`:
```
DB_POSTGRESQL=postgresql+asyncpg://usuario:password@localhost:5432/nombre_base_datos
```
3. Verificar que la base de datos y la tabla `producto` existan

---

### Error 5: `Error loading ASGI app. Could not import module "main"`

```
ERROR:    Error loading ASGI app. Could not import module "main".
```

**Causa:** No existe el archivo `main.py` en el directorio actual, o hay un error de sintaxis en el archivo.

**Solucion:**
1. Verificar que `main.py` existe en el directorio donde ejecutas uvicorn
2. Verificar que no haya errores de sintaxis: `python main.py` (si hay errores, Python los muestra)

---

## Resumen de la Parte 6

### Archivo creado

| # | Archivo | Capa | Lineas | Proposito |
|---|---------|------|--------|-----------|
| 1 | `main.py` | Punto de entrada | ~25 | Crea la app FastAPI, registra el router de producto, define endpoint raiz |

### Que hace `main.py`

| Paso | Codigo | Proposito |
|------|--------|-----------|
| 1 | `from fastapi import FastAPI` | Importa la clase principal del framework |
| 2 | `from controllers... import router as producto_router` | Importa el router con los 5 endpoints |
| 3 | `app = FastAPI(title=..., description=..., version=...)` | Crea la aplicacion con metadatos para la documentacion |
| 4 | `app.include_router(producto_router)` | Registra los 5 endpoints de producto en la app |
| 5 | `@app.get("/")` | Define un endpoint raiz de verificacion |

### Comando de ejecucion

```bash
uvicorn main:app --reload
```

### URLs de la API

| URL | Descripcion |
|-----|-------------|
| `http://127.0.0.1:8000/` | Verificacion: la API esta activa |
| `http://127.0.0.1:8000/docs` | Swagger UI: documentacion interactiva |
| `http://127.0.0.1:8000/redoc` | ReDoc: documentacion de solo lectura |
| `http://127.0.0.1:8000/api/producto/` | Endpoints de productos |

### CRUD completo probado

| Operacion | Metodo HTTP | Endpoint | Codigo exito |
|-----------|-------------|----------|-------------|
| **C**rear | POST | `/api/producto/` | 200 |
| **R**ead (listar) | GET | `/api/producto/` | 200 / 204 |
| **R**ead (uno) | GET | `/api/producto/{codigo}` | 200 |
| **U**pdate | PUT | `/api/producto/{codigo}` | 200 |
| **D**elete | DELETE | `/api/producto/{codigo}` | 200 |

### Arquitectura completa del tutorial

```
main.py                              ← PARTE 6 (este archivo)
  │
  └── app.include_router(producto_router)
        │
        ▼
controllers/producto_controller.py   ← Parte 5 (capa de presentacion)
  │  5 endpoints: GET, GET/{codigo}, POST, PUT, DELETE
  │  Usa modelo Pydantic: models/producto.py
  │
  └── crear_servicio_producto()
        │
        ▼
servicios/fabrica_repositorios.py    ← Parte 4 (fabrica)
  │  Crea el servicio con su repositorio inyectado
  │
  └── ServicioProducto(repo)
        │
        ▼
servicios/servicio_producto.py       ← Parte 4 (capa de negocio)
  │  Valida datos y delega al repositorio
  │
  └── self._repo.listar() / .crear() / .actualizar() / .eliminar()
        │
        ▼
repositorios/repositorio_producto_postgresql.py  ← Parte 3 (capa de datos)
  │  Hereda de base_repositorio_postgresql.py
  │
  └── SQL: SELECT / INSERT / UPDATE / DELETE
        │
        ▼
PostgreSQL                           ← Parte 2 (base de datos)
```

---

## Siguiente paso

Con la Parte 6 has completado el **tutorial completo**. Tienes una API REST CRUD funcional con:

- Arquitectura de 3 capas (datos, negocio, presentacion)
- Patrones de diseno (Repository, Factory, Dependency Injection, DTO)
- Validacion automatica con Pydantic
- Documentacion automatica con Swagger UI y ReDoc
- 5 endpoints funcionales para la tabla `producto`

Para expandir el proyecto, puedes:
1. Agregar mas entidades (cliente, factura, vendedor) siguiendo el mismo patron
2. Agregar soporte para MySQL/MariaDB creando un nuevo repositorio base
3. Agregar autenticacion con JWT
4. Agregar pruebas unitarias con pytest
5. Desplegar en un servidor con Docker

---

> **Nota:** Este tutorial cubrio la entidad `producto`. El proyecto original completo (`apifacturas_fastapi_tutorial`) tiene 13 entidades siguiendo exactamente la misma arquitectura. Agregar una nueva entidad es cuestion de crear 4 archivos (modelo Pydantic, repositorio, servicio, controller) y registrar el router en `main.py` con una linea adicional de `include_router()`.
