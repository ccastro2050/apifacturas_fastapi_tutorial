# PARTE 7 — Flujo Completo y Recapitulacion

> **Parte 7 de 7** — Esta es la parte FINAL del tutorial.
> En las partes anteriores construimos cada capa por separado.
> Ahora vamos a ver como todo trabaja junto: desde que el cliente
> envia una peticion HTTP hasta que PostgreSQL ejecuta el SQL y la
> respuesta regresa al navegador.

---

## 7.1 Flujo completo de una peticion POST /api/producto/

Cuando un cliente (Postman, Swagger UI, o un frontend) envia un `POST /api/producto/` con un JSON en el body, la peticion atraviesa **todas las capas** de nuestra arquitectura. Veamos el recorrido completo paso a paso.

### 7.1.1 Diagrama del flujo POST (crear producto)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLIENTE HTTP                                     │
│    Postman / Swagger UI / Frontend                                       │
│                                                                          │
│    POST http://localhost:8000/api/producto/                              │
│    Content-Type: application/json                                        │
│    Body: {                                                               │
│        "codigo": "PR999",                                                │
│        "nombre": "Teclado Mecanico RGB",                                 │
│        "stock": 50,                                                      │
│        "valorunitario": 25000.0                                          │
│    }                                                                     │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           │  (1) Peticion HTTP viaja por la red
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  UVICORN (Servidor ASGI)                                                 │
│                                                                          │
│  Recibe la peticion HTTP en el puerto 8000.                              │
│  La pasa a FastAPI para que la procese.                                   │
│  (Equivalente a Kestrel en ASP.NET o Tomcat en Java)                     │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           │  (2) FastAPI busca la ruta que coincida
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  FASTAPI — Enrutamiento y Validacion                                     │
│                                                                          │
│  1. Busca en los routers registrados: POST /api/producto/ ──> encontrado │
│  2. Identifica el handler: crear_producto() en producto_controller.py    │
│  3. Ve que el parametro es "producto: Producto" (modelo Pydantic)        │
│  4. PYDANTIC valida el JSON del body automaticamente:                    │
│     - codigo: str    ──> "PR999"          OK (es string)                 │
│     - nombre: str    ──> "Teclado..."     OK (es string)                 │
│     - stock: int     ──> 50               OK (es entero)                 │
│     - valorunitario: float ──> 25000.0    OK (es decimal)               │
│                                                                          │
│  Si la validacion FALLA: retorna 422 SIN ejecutar el handler.            │
│  Si la validacion PASA:  crea objeto Producto y llama al handler.        │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           │  (3) Llama a crear_producto(producto=Producto(...))
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  CAPA DE PRESENTACION — producto_controller.py                           │
│  Archivo: controllers/producto_controller.py                             │
│  Funcion: crear_producto(producto: Producto, esquema: str | None)        │
│                                                                          │
│  Paso 3a: datos = producto.model_dump()                                  │
│           ──> {"codigo": "PR999", "nombre": "Teclado Mecanico RGB",      │
│                "stock": 50, "valorunitario": 25000.0}                    │
│                                                                          │
│  Paso 3b: servicio = crear_servicio_producto()  ──> llama a la Factory   │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           │  (4) Factory crea todo el stack
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  FACTORY — fabrica_repositorios.py                                       │
│  Archivo: servicios/fabrica_repositorios.py                              │
│  Funcion: crear_servicio_producto()                                      │
│                                                                          │
│  Paso 4a: proveedor, nombre = _obtener_proveedor()                       │
│           ├── ProveedorConexion() ──> lee config.py ──> lee .env         │
│           ├── DB_PROVIDER = "postgres"                                   │
│           └── retorna (proveedor_obj, "postgres")                        │
│                                                                          │
│  Paso 4b: repo = _crear_repo_entidad(_REPOS_PRODUCTO, proveedor, nombre)│
│           ├── _REPOS_PRODUCTO["postgres"]                                │
│           │   ──> clase RepositorioProductoPostgreSQL                    │
│           └── RepositorioProductoPostgreSQL(proveedor) ──> instancia     │
│                                                                          │
│  Paso 4c: return ServicioProducto(repo)                                  │
│           ──> Inyecta el repositorio en el servicio (DI por constructor)  │
│           ──> Retorna servicio listo para usar                           │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           │  (5) Controller llama: servicio.crear(datos, esquema)
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  CAPA DE NEGOCIO — servicio_producto.py                                  │
│  Archivo: servicios/servicio_producto.py                                 │
│  Metodo: crear(datos: dict, esquema: str | None)                         │
│                                                                          │
│  Paso 5a: Valida que datos no este vacio                                 │
│           ──> {"codigo": "PR999", ...} tiene 4 claves ──> OK             │
│                                                                          │
│  Paso 5b: Normaliza esquema                                              │
│           ──> esquema es None ──> esquema_norm = None                    │
│                                                                          │
│  Paso 5c: return await self._repo.crear(datos, esquema_norm)             │
│           ──> Delega al repositorio (NO ejecuta SQL aqui)                │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           │  (6) Servicio llama: repo.crear(datos, None)
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  CAPA DE DATOS — repositorio_producto_postgresql.py                      │
│  Archivo: repositorios/producto/repositorio_producto_postgresql.py       │
│  Metodo: crear(datos, esquema)                                           │
│                                                                          │
│  Paso 6a: return await self._crear(self.TABLA, datos, esquema)           │
│           ──> self.TABLA = "producto"                                    │
│           ──> Delega al metodo heredado _crear() de la clase base        │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           │  (7) Metodo heredado _crear() de BaseRepositorioPostgreSQL
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  CAPA DE DATOS — base_repositorio_postgresql.py                          │
│  Archivo: repositorios/base_repositorio_postgresql.py                    │
│  Metodo: _crear(nombre_tabla, datos, esquema)                            │
│                                                                          │
│  Paso 7a: esquema_final = "public"  (default porque esquema era None)    │
│                                                                          │
│  Paso 7b: Construye SQL dinamicamente:                                   │
│           columnas = '"codigo", "nombre", "stock", "valorunitario"'      │
│           parametros = ':codigo, :nombre, :stock, :valorunitario'        │
│           SQL = INSERT INTO "public"."producto"                          │
│                 ("codigo", "nombre", "stock", "valorunitario")           │
│                 VALUES (:codigo, :nombre, :stock, :valorunitario)        │
│                                                                          │
│  Paso 7c: Convierte tipos si es necesario:                               │
│           "PR999" ──> str (ya es string, no convierte)                   │
│           50 ──> int (ya es int, no convierte)                           │
│           25000.0 ──> float (ya es float, no convierte)                  │
│                                                                          │
│  Paso 7d: engine = await self._obtener_engine()                          │
│           ──> create_async_engine(cadena_conexion) ──> pool asyncpg      │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           │  (8) SQLAlchemy ejecuta el query via asyncpg
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  SQLALCHEMY ASYNC + ASYNCPG                                              │
│                                                                          │
│  async with engine.begin() as conn:      ──> Abre transaccion            │
│      result = await conn.execute(sql, valores)                           │
│                                                                          │
│  El SQL que se envia a PostgreSQL:                                       │
│  INSERT INTO "public"."producto"                                         │
│  ("codigo", "nombre", "stock", "valorunitario")                          │
│  VALUES ('PR999', 'Teclado Mecanico RGB', 50, 25000.0)                   │
│                                                                          │
│  Si exito: COMMIT automatico (engine.begin())                            │
│  Si error: ROLLBACK automatico                                           │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           │  (9) PostgreSQL ejecuta el INSERT
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  POSTGRESQL — bdfacturas_postgres_local                                   │
│                                                                          │
│  Ejecuta: INSERT INTO "public"."producto" (...) VALUES (...)             │
│  Resultado: 1 fila insertada (rowcount = 1)                              │
│                                                                          │
│  La tabla producto ahora tiene una nueva fila:                           │
│  | codigo | nombre               | stock | valorunitario |               │
│  |--------|----------------------|-------|---------------|               │
│  | PR999  | Teclado Mecanico RGB | 50    | 25000.00      |               │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           │  (10) La respuesta SUBE por todas las capas
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  RESPUESTA SUBIENDO POR LAS CAPAS                                        │
│                                                                          │
│  PostgreSQL ──> rowcount = 1                                             │
│       ▲                                                                  │
│  base_repositorio_postgresql._crear()                                    │
│       ──> return result.rowcount > 0 ──> True                            │
│       ▲                                                                  │
│  repositorio_producto_postgresql.crear()                                  │
│       ──> return await self._crear(...) ──> True                         │
│       ▲                                                                  │
│  servicio_producto.crear()                                                │
│       ──> return await self._repo.crear(...) ──> True                    │
│       ▲                                                                  │
│  producto_controller.crear_producto()                                     │
│       ──> creado = True                                                  │
│       ──> return {"estado": 200, "mensaje": "Producto creado             │
│                    exitosamente.", "datos": {...}}                        │
│       ▲                                                                  │
│  FastAPI ──> Serializa dict a JSON ──> HTTP 200 OK                       │
│       ▲                                                                  │
│  uvicorn ──> Envia la respuesta HTTP al cliente                          │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  CLIENTE HTTP — Respuesta recibida                                       │
│                                                                          │
│  HTTP/1.1 200 OK                                                         │
│  Content-Type: application/json                                          │
│                                                                          │
│  {                                                                       │
│      "estado": 200,                                                      │
│      "mensaje": "Producto creado exitosamente.",                         │
│      "datos": {                                                          │
│          "codigo": "PR999",                                              │
│          "nombre": "Teclado Mecanico RGB",                               │
│          "stock": 50,                                                    │
│          "valorunitario": 25000.0                                        │
│      }                                                                   │
│  }                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

### 7.1.2 Resumen del flujo POST en una linea

```
Cliente ──> uvicorn ──> FastAPI (Pydantic valida) ──> crear_producto()
──> model_dump() ──> crear_servicio_producto() [Factory]
──> servicio.crear() [valida datos] ──> repo.crear() ──> self._crear()
──> INSERT INTO ... ──> PostgreSQL ──> rowcount=1 ──> True
──> {"estado": 200, "mensaje": "Producto creado exitosamente."}
```

### 7.1.3 Diagrama del flujo GET /api/producto/PR001 (obtener uno)

El flujo de lectura es mas corto porque no hay `model_dump()` ni transaccion `begin()`. Veamos la diferencia:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  CLIENTE HTTP                                                            │
│  GET http://localhost:8000/api/producto/PR001                            │
│  (Sin body — el codigo va en la URL como path parameter)                 │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  FASTAPI — Enrutamiento                                                  │
│                                                                          │
│  Ruta: GET /api/producto/{codigo} ──> obtener_producto(codigo="PR001")   │
│  No hay body ──> No hay validacion Pydantic                              │
│  "PR001" viene de la URL como path parameter (str)                       │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  CONTROLLER — obtener_producto(codigo="PR001")                           │
│                                                                          │
│  servicio = crear_servicio_producto()  ──> Factory crea stack            │
│  filas = await servicio.obtener_por_codigo("PR001", esquema)             │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  SERVICIO — obtener_por_codigo("PR001", None)                            │
│                                                                          │
│  Valida: "PR001" no esta vacio ──> OK                                    │
│  Normaliza: esquema_norm = None                                          │
│  Delega: return await self._repo.obtener_por_codigo("PR001", None)       │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  REPOSITORIO — obtener_por_codigo("PR001", None)                         │
│                                                                          │
│  Delega: self._obtener_por_clave("producto", "codigo", "PR001", None)    │
│                                                                          │
│  SQL: SELECT * FROM "public"."producto" WHERE "codigo" = :valor          │
│  Parametro: {"valor": "PR001"}                                           │
│                                                                          │
│  NOTA: Usa engine.connect() (solo lectura), NO engine.begin()            │
│  (no necesita transaccion porque es un SELECT)                           │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  POSTGRESQL ──> Encuentra la fila ──> retorna resultado                  │
│                                                                          │
│  Resultado: [{"codigo": "PR001", "nombre": "Laptop", "stock": 20,       │
│               "valorunitario": 2500000.0}]                               │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  RESPUESTA AL CLIENTE                                                    │
│                                                                          │
│  HTTP/1.1 200 OK                                                         │
│  {                                                                       │
│      "tabla": "producto",                                                │
│      "total": 1,                                                         │
│      "datos": [                                                          │
│          {"codigo": "PR001", "nombre": "Laptop",                         │
│           "stock": 20, "valorunitario": 2500000.0}                       │
│      ]                                                                   │
│  }                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

### 7.1.4 Diferencias clave entre POST y GET

| Aspecto | POST /api/producto/ | GET /api/producto/{codigo} |
|---------|--------------------|-----------------------------|
| Body JSON | Si (datos del producto) | No (codigo en la URL) |
| Validacion Pydantic | Si (valida 4 campos) | No (solo path parameter) |
| model_dump() | Si (Producto a dict) | No necesario |
| Servicio valida | Datos no vacios | Codigo no vacio |
| Metodo repo | `crear()` → `_crear()` | `obtener_por_codigo()` → `_obtener_por_clave()` |
| SQL generado | INSERT INTO ... VALUES | SELECT * ... WHERE |
| Tipo conexion | `engine.begin()` (transaccion) | `engine.connect()` (solo lectura) |
| Retorna | `bool` (True/False) | `list[dict]` (filas) |

---

## 7.2 Mapa de archivos y capas

Nuestro proyecto tiene **23 archivos** en total (20 archivos Python + 3 archivos de configuracion). Aqui esta el mapa completo organizado por capa:

### 7.2.1 Tabla completa de archivos

| # | Archivo | Capa | Lineas | Proposito |
|---|---------|------|--------|-----------|
| 1 | `main.py` | Entrada | 77 | Punto de entrada. Crea la app FastAPI, registra el router de producto, define endpoint raiz `/`. |
| 2 | `config.py` | Configuracion | 152 | Lee `.env` con pydantic-settings. Patron Singleton con `@lru_cache`. Clases `Settings` y `DatabaseSettings`. |
| 3 | `.env` | Configuracion | 39 | Variables de entorno: `ENVIRONMENT`, `DEBUG`, `DB_PROVIDER`, `DB_POSTGRES` (cadena de conexion). |
| 4 | `.gitignore` | Configuracion | 30 | Archivos ignorados por git: `venv/`, `__pycache__/`, `.env`, `.vscode/`. |
| 5 | `requirements.txt` | Configuracion | 70 | 7 dependencias: fastapi, uvicorn, pydantic, pydantic-settings, python-dotenv, asyncpg, sqlalchemy, greenlet. |
| 6 | `controllers/__init__.py` | Presentacion | 0 | Paquete controllers (archivo vacio, necesario para que Python reconozca la carpeta). |
| 7 | `controllers/producto_controller.py` | Presentacion | 218 | 5 endpoints CRUD con `APIRouter`. Manejo de errores HTTP (400, 404, 500). Usa Factory. |
| 8 | `models/__init__.py` | Presentacion | 29 | Re-exporta `Producto` para imports cortos: `from models import Producto`. |
| 9 | `models/producto.py` | Presentacion | 26 | Modelo Pydantic con 4 campos: `codigo`, `nombre`, `stock`, `valorunitario`. Validacion automatica. |
| 10 | `servicios/__init__.py` | Negocio | 0 | Paquete servicios. |
| 11 | `servicios/abstracciones/__init__.py` | Negocio | 0 | Paquete abstracciones. |
| 12 | `servicios/abstracciones/i_proveedor_conexion.py` | Negocio | 24 | Protocol: contrato con `proveedor_actual` (property) y `obtener_cadena_conexion()`. |
| 13 | `servicios/abstracciones/i_servicio_producto.py` | Negocio | 47 | Protocol: contrato con 5 metodos async (`listar`, `obtener_por_codigo`, `crear`, `actualizar`, `eliminar`). |
| 14 | `servicios/conexion/__init__.py` | Negocio | 0 | Paquete conexion. |
| 15 | `servicios/conexion/proveedor_conexion.py` | Negocio | 56 | Lee `DB_PROVIDER` y retorna la cadena de conexion correspondiente. Diccionario de cadenas por proveedor. |
| 16 | `servicios/servicio_producto.py` | Negocio | 58 | 5 metodos de negocio. Valida datos vacios, normaliza esquema. Delega al repositorio. |
| 17 | `servicios/fabrica_repositorios.py` | Negocio | 57 | Factory: `crear_servicio_producto()`. Diccionario `_REPOS_PRODUCTO` mapea proveedor a clase. |
| 18 | `repositorios/__init__.py` | Datos | 23 | Re-exporta `BaseRepositorioPostgreSQL` para imports cortos. |
| 19 | `repositorios/abstracciones/__init__.py` | Datos | 0 | Paquete abstracciones. |
| 20 | `repositorios/abstracciones/i_repositorio_producto.py` | Datos | 60 | Protocol: contrato con 5 metodos async (`obtener_todos`, `obtener_por_codigo`, `crear`, `actualizar`, `eliminar`). |
| 21 | `repositorios/base_repositorio_postgresql.py` | Datos | 373 | Clase base generica. SQL con SQLAlchemy: `_obtener_filas`, `_obtener_por_clave`, `_crear`, `_actualizar`, `_eliminar`. Deteccion y conversion de tipos. |
| 22 | `repositorios/producto/__init__.py` | Datos | 19 | Re-exporta `RepositorioProductoPostgreSQL` para imports cortos. |
| 23 | `repositorios/producto/repositorio_producto_postgresql.py` | Datos | 53 | Repositorio concreto: define `TABLA = "producto"`, `CLAVE_PRIMARIA = "codigo"`. 5 metodos delegan a la clase base. |

### 7.2.2 Resumen por capa

| Capa | Archivos Python | Lineas de codigo | Archivos config |
|------|----------------|-------------------|-----------------|
| Entrada | 1 (`main.py`) | 77 | — |
| Configuracion | 1 (`config.py`) | 152 | 3 (`.env`, `.gitignore`, `requirements.txt`) |
| Presentacion | 4 (controller, modelo, 2 `__init__`) | 273 | — |
| Negocio | 8 (servicio, factory, proveedor, 2 interfaces, 3 `__init__`) | 242 | — |
| Datos | 6 (base repo, repo concreto, interfaz, 3 `__init__`) | 528 | — |
| **TOTAL** | **20 archivos Python** | **~1272 lineas** | **3 archivos config** |

> **Observacion**: La capa de datos tiene mas lineas porque `base_repositorio_postgresql.py` (373 lineas) contiene toda la logica SQL generica reutilizable. Es la inversion correcta: escribimos SQL generico UNA vez, y cada entidad nueva solo necesita ~50 lineas.

---

## 7.3 Tabla de patrones de diseno implementados

A lo largo de las 7 partes, implementamos **8 patrones de diseno**. Aqui esta el resumen completo con su equivalencia en .NET para quienes vengan de ese ecosistema:

| # | Patron | Archivo(s) | Que hace | Equivalencia .NET |
|---|--------|-----------|----------|-------------------|
| 1 | **Repository** | `base_repositorio_postgresql.py`, `repositorio_producto_postgresql.py` | Encapsula TODO el acceso a datos detras de una interfaz limpia. El controller jamas toca SQL. El SQL vive SOLO en la capa de datos. | `IRepository<T>` + Entity Framework Core |
| 2 | **Factory** | `fabrica_repositorios.py` | Crea el repositorio y servicio correctos segun `DB_PROVIDER`. Centraliza la decision de QUE objetos crear. El controller solo llama a `crear_servicio_producto()` sin saber que BD se usa. | `IServiceCollection.AddScoped<IRepo, RepoPostgres>()` |
| 3 | **Service Layer** | `servicio_producto.py` | Capa intermedia entre controller y repositorio. Valida que los datos no esten vacios, normaliza parametros (`esquema.strip()`), y delega al repositorio. Separa la logica de NEGOCIO de la logica de PRESENTACION y de DATOS. | Application Services / MediatR handlers |
| 4 | **Protocol (Interface)** | `i_proveedor_conexion.py`, `i_repositorio_producto.py`, `i_servicio_producto.py` | Contratos que definen QUE debe hacer una clase sin decir COMO. Usan `typing.Protocol` (structural typing): si una clase tiene los mismos metodos, cumple el contrato sin heredar. | `interface IProductoRepository { ... }` |
| 5 | **Template Method** | `base_repositorio_postgresql.py` → `repositorio_producto_postgresql.py` | La clase base define el algoritmo generico (`_crear`, `_obtener_filas`, `_actualizar`, `_eliminar`). La subclase solo define `TABLA` y `CLAVE_PRIMARIA`. El "esqueleto" esta en el padre, los "detalles" en el hijo. | `abstract class BaseRepository<T>` + `override` |
| 6 | **Dependency Injection** | `ServicioProducto(repo)`, `BaseRepositorioPostgreSQL(proveedor)` | Las clases reciben sus dependencias por CONSTRUCTOR, no las crean internamente. Esto permite cambiar implementaciones sin modificar la clase que las usa. | Constructor injection con `services.AddScoped()` |
| 7 | **Singleton** | `config.py` → `@lru_cache` en `get_settings()` | La configuracion se lee del disco UNA sola vez (primera llamada). Las llamadas posteriores retornan el objeto cacheado sin leer el `.env` de nuevo. | `services.AddSingleton<Settings>()` |
| 8 | **Strategy** | `_REPOS_PRODUCTO` dict en `fabrica_repositorios.py` | Diferentes implementaciones de repositorio intercambiables en tiempo de ejecucion. Cambias `DB_PROVIDER` en `.env` y automaticamente se usa otro repositorio. La estrategia se selecciona por configuracion, no por codigo. | Strategy pattern con DI container |

### 7.3.1 Como se relacionan los patrones entre si

```
     Singleton (config.py)
         │
         │ lee .env UNA vez
         ▼
     Factory (fabrica_repositorios.py)
         │
         ├── usa Strategy (dict _REPOS_PRODUCTO)
         │   para elegir QUE repositorio crear
         │
         ├── crea Repository (repositorio_producto_postgresql.py)
         │   que usa Template Method (hereda de base_repositorio_postgresql.py)
         │   y cumple Protocol (i_repositorio_producto.py)
         │
         └── inyecta via Dependency Injection
             en Service Layer (servicio_producto.py)
             que cumple Protocol (i_servicio_producto.py)
```

> **Analogia**: Piensa en la Factory como un restaurante. El menu (Strategy dict) decide que plato servir segun lo que el cliente pida (DB_PROVIDER). La cocina (Repository) prepara el plato siguiendo una receta base (Template Method). El mesero (Service Layer) verifica que el pedido sea valido antes de pasarlo a la cocina. Y el contrato con el cliente (Protocol/Interface) garantiza que el restaurante siempre sirva los mismos tipos de platos, sin importar quien cocine.

---

## 7.4 Principios SOLID aplicados — Tabla resumen

Los 5 principios SOLID son la base teorica que guia las decisiones de arquitectura de este proyecto:

| Principio | Nombre completo | Donde se aplica | Ejemplo concreto |
|-----------|----------------|-----------------|-------------------|
| **S** | Single Responsibility (Responsabilidad Unica) | Cada archivo tiene UNA responsabilidad | `producto_controller.py`: solo maneja HTTP y errores. `servicio_producto.py`: solo valida y normaliza. `base_repositorio_postgresql.py`: solo ejecuta SQL. Ninguno invade el territorio del otro. |
| **O** | Open/Closed (Abierto/Cerrado) | `fabrica_repositorios.py` + `_REPOS_PRODUCTO` dict | Para agregar soporte MySQL: creas una clase nueva + agregas 1 linea al diccionario. **CERO cambios** en controller, servicio, modelo o interfaces. El sistema esta ABIERTO a extension y CERRADO a modificacion. |
| **L** | Liskov Substitution (Sustitucion de Liskov) | Cualquier repo que cumpla el Protocol funciona | Cambias `DB_PROVIDER` de `"postgres"` a `"mysql"` y el controller **no se entera**. El nuevo repositorio es 100% sustituible porque cumple el mismo contrato (`IRepositorioProducto`). |
| **I** | Interface Segregation (Segregacion de Interfaces) | 3 interfaces separadas y especificas | `IRepositorioProducto` (5 metodos de datos), `IServicioProducto` (5 metodos de negocio), `IProveedorConexion` (1 property + 1 metodo). Cada interfaz define SOLO lo que su consumidor necesita. No hay una "super interfaz" con 30 metodos. |
| **D** | Dependency Inversion (Inversion de Dependencias) | `ServicioProducto(repositorio)`, `BaseRepositorioPostgreSQL(proveedor)` | El servicio depende de la ABSTRACCION (Protocol `IRepositorioProducto`), **no** de la clase concreta `RepositorioProductoPostgreSQL`. Si manana cambias de PostgreSQL a MySQL, el servicio no se modifica. |

### 7.4.1 Visualizacion: sin SOLID vs. con SOLID

**Sin SOLID** (todo acoplado):
```
Controller ──> SQL directo a PostgreSQL
   (si cambias la BD, reescribes TODO el controller)
```

**Con SOLID** (nuestro proyecto):
```
Controller ──> Servicio ──> Repositorio (Protocol) ──> PostgreSQL
                                    │
                                    └──> MySQL (solo agregar clase)
                                    └──> SQLServer (solo agregar clase)
   (el controller y servicio JAMAS se modifican)
```

---

## 7.5 Como extender el proyecto — Agregar soporte MySQL

Una de las mayores fortalezas de esta arquitectura es lo FACIL que es agregar soporte para otra base de datos. Veamos paso a paso como agregar MySQL **sin tocar el controller, servicio, modelo ni interfaces**.

### 7.5.1 Paso 1 — Crear 1 archivo nuevo

Archivo: `repositorios/producto/repositorio_producto_mysql.py`

```python
"""Repositorio de producto para MySQL/MariaDB."""

from repositorios.base_repositorio_mysql import BaseRepositorioMysqlMariaDB
# Necesitarias crear tambien una clase base para MySQL (similar a la de PostgreSQL)
# con las diferencias de sintaxis SQL (backticks en vez de comillas dobles, etc.)


class RepositorioProductoMysqlMariaDB(BaseRepositorioMysqlMariaDB):
    """Acceso a datos de producto en MySQL/MariaDB."""

    TABLA = "producto"              # Mismo nombre de tabla
    CLAVE_PRIMARIA = "codigo"       # Misma clave primaria

    # Los 5 metodos son IDENTICOS en estructura al de PostgreSQL:
    async def obtener_todos(self, esquema=None, limite=None):
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_codigo(self, codigo, esquema=None):
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )

    async def crear(self, datos, esquema=None):
        return await self._crear(self.TABLA, datos, esquema)

    async def actualizar(self, codigo, datos, esquema=None):
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), datos, esquema
        )

    async def eliminar(self, codigo, esquema=None):
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )
```

### 7.5.2 Paso 2 — Agregar 1 linea al diccionario de la Factory

Archivo: `servicios/fabrica_repositorios.py`

**ANTES:**

```python
from repositorios.producto import RepositorioProductoPostgreSQL

_REPOS_PRODUCTO = {
    "postgres": RepositorioProductoPostgreSQL,
    "postgresql": RepositorioProductoPostgreSQL,
}
```

**DESPUES:**

```python
from repositorios.producto import RepositorioProductoPostgreSQL
from repositorios.producto.repositorio_producto_mysql import RepositorioProductoMysqlMariaDB  # NUEVO

_REPOS_PRODUCTO = {
    "postgres": RepositorioProductoPostgreSQL,
    "postgresql": RepositorioProductoPostgreSQL,
    "mysql": RepositorioProductoMysqlMariaDB,       # <── 1 LINEA NUEVA
    "mariadb": RepositorioProductoMysqlMariaDB,      # <── Alias opcional
}
```

### 7.5.3 Paso 3 — Agregar cadena de conexion

Archivo: `config.py` — agregar campo en `DatabaseSettings`:

```python
class DatabaseSettings(BaseSettings):
    # ... campos existentes ...
    postgres: str = Field(default='')
    mysql: str = Field(default='')       # <── NUEVO: lee DB_MYSQL del .env
```

Archivo: `.env` — agregar variable:

```bash
# Cadena de conexion para MySQL
DB_MYSQL=mysql+aiomysql://root:password@localhost:3306/bdfacturas_mysql_local
```

Archivo: `servicios/conexion/proveedor_conexion.py` — agregar al diccionario:

```python
cadenas = {
    "postgres": db_config.postgres,
    "postgresql": db_config.postgres,
    "mysql": db_config.mysql,           # <── NUEVO
    "mariadb": db_config.mysql,         # <── Alias
}
```

### 7.5.4 Paso 4 — Cambiar 1 variable en .env

```bash
# ANTES:
DB_PROVIDER=postgres

# DESPUES:
DB_PROVIDER=mysql
```

### 7.5.5 Lo que NO se toca

| Archivo | Se modifica? |
|---------|-------------|
| `controllers/producto_controller.py` | **NO** |
| `models/producto.py` | **NO** |
| `servicios/servicio_producto.py` | **NO** |
| `servicios/abstracciones/i_servicio_producto.py` | **NO** |
| `servicios/abstracciones/i_proveedor_conexion.py` | **NO** |
| `repositorios/abstracciones/i_repositorio_producto.py` | **NO** |
| `repositorios/producto/repositorio_producto_postgresql.py` | **NO** |
| `main.py` | **NO** |

> **Este es el poder de SOLID + arquitectura de 3 capas**: agregar una base de datos nueva requiere crear 1 archivo + modificar 3 archivos de configuracion/factory. Los 8 archivos que contienen la logica de negocio y presentacion permanecen INTACTOS. En un proyecto sin esta arquitectura, tendrias que reescribir el controller completo.

---

## 7.6 Como agregar una nueva entidad (ejemplo: cliente)

Supongamos que queremos agregar una entidad `cliente` al proyecto. Gracias a la arquitectura de 3 capas, el proceso es **mecanico** — seguimos el MISMO patron que usamos para `producto`.

### 7.6.1 Archivos a crear (8 nuevos)

| # | Archivo a crear | Capa | Basado en |
|---|----------------|------|-----------|
| 1 | `models/cliente.py` | Presentacion | Copiar estructura de `models/producto.py` |
| 2 | `repositorios/abstracciones/i_repositorio_cliente.py` | Datos | Copiar estructura de `i_repositorio_producto.py` |
| 3 | `repositorios/cliente/__init__.py` | Datos | Copiar estructura de `repositorios/producto/__init__.py` |
| 4 | `repositorios/cliente/repositorio_cliente_postgresql.py` | Datos | Copiar estructura de `repositorio_producto_postgresql.py` |
| 5 | `servicios/abstracciones/i_servicio_cliente.py` | Negocio | Copiar estructura de `i_servicio_producto.py` |
| 6 | `servicios/servicio_cliente.py` | Negocio | Copiar estructura de `servicio_producto.py` |
| 7 | `controllers/cliente_controller.py` | Presentacion | Copiar estructura de `producto_controller.py` |
| 8 | `repositorios/cliente/` (carpeta) | Datos | Nueva carpeta |

### 7.6.2 Archivos a modificar (3 existentes)

| # | Archivo a modificar | Cambio |
|---|---------------------|--------|
| 1 | `models/__init__.py` | Agregar: `from .cliente import Cliente` |
| 2 | `servicios/fabrica_repositorios.py` | Agregar: funcion `crear_servicio_cliente()` y dict `_REPOS_CLIENTE` |
| 3 | `main.py` | Agregar: `app.include_router(cliente_router)` |

### 7.6.3 Codigo de cada archivo nuevo

**1. `models/cliente.py`** — Modelo Pydantic:

```python
"""Modelo Pydantic para la tabla cliente."""

from pydantic import BaseModel


class Cliente(BaseModel):
    """Representa un cliente en la base de datos."""
    codigo: str          # PK: VARCHAR(30)
    nombre: str          # VARCHAR(100)
    direccion: str | None = None   # VARCHAR(200)
    telefono: str | None = None    # VARCHAR(20)
```

**2. `models/__init__.py`** — Agregar re-export:

```python
from .producto import Producto
from .cliente import Cliente      # <── NUEVO
```

**3. `repositorios/abstracciones/i_repositorio_cliente.py`** — Protocol:

```python
"""Contrato del repositorio especifico para cliente."""

from typing import Protocol, Any, Optional


class IRepositorioCliente(Protocol):
    """Contrato para el repositorio de cliente."""

    async def obtener_todos(self, esquema: Optional[str] = None,
                            limite: Optional[int] = None) -> list[dict[str, Any]]: ...
    async def obtener_por_codigo(self, codigo: str,
                                  esquema: Optional[str] = None) -> list[dict[str, Any]]: ...
    async def crear(self, datos: dict[str, Any],
                    esquema: Optional[str] = None) -> bool: ...
    async def actualizar(self, codigo: str, datos: dict[str, Any],
                         esquema: Optional[str] = None) -> int: ...
    async def eliminar(self, codigo: str,
                       esquema: Optional[str] = None) -> int: ...
```

**4. `repositorios/cliente/repositorio_cliente_postgresql.py`** — Repo concreto:

```python
"""Repositorio de cliente para PostgreSQL."""

from repositorios.base_repositorio_postgresql import BaseRepositorioPostgreSQL


class RepositorioClientePostgreSQL(BaseRepositorioPostgreSQL):
    """Acceso a datos de cliente en PostgreSQL."""

    TABLA = "cliente"              # <── Cambia la tabla
    CLAVE_PRIMARIA = "codigo"      # <── Cambia (o no) la PK

    async def obtener_todos(self, esquema=None, limite=None):
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_codigo(self, codigo, esquema=None):
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )

    async def crear(self, datos, esquema=None):
        return await self._crear(self.TABLA, datos, esquema)

    async def actualizar(self, codigo, datos, esquema=None):
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), datos, esquema
        )

    async def eliminar(self, codigo, esquema=None):
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )
```

**5. `repositorios/cliente/__init__.py`** — Re-export:

```python
"""Repositorios especificos de cliente."""
from .repositorio_cliente_postgresql import RepositorioClientePostgreSQL
```

**6. `servicios/abstracciones/i_servicio_cliente.py`** — Protocol del servicio:

```python
"""Contrato del servicio especifico para cliente."""

from typing import Protocol, Any, Optional


class IServicioCliente(Protocol):
    async def listar(self, esquema: Optional[str] = None,
                     limite: Optional[int] = None) -> list[dict[str, Any]]: ...
    async def obtener_por_codigo(self, codigo: str,
                                  esquema: Optional[str] = None) -> list[dict[str, Any]]: ...
    async def crear(self, datos: dict[str, Any],
                    esquema: Optional[str] = None) -> bool: ...
    async def actualizar(self, codigo: str, datos: dict[str, Any],
                         esquema: Optional[str] = None) -> int: ...
    async def eliminar(self, codigo: str,
                       esquema: Optional[str] = None) -> int: ...
```

**7. `servicios/servicio_cliente.py`** — Servicio de negocio:

```python
"""Servicio especifico para la entidad cliente."""

from typing import Any


class ServicioCliente:
    """Logica de negocio para cliente."""

    def __init__(self, repositorio):
        if repositorio is None:
            raise ValueError("repositorio no puede ser None.")
        self._repo = repositorio

    async def listar(self, esquema=None, limite=None):
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        limite_norm = limite if limite and limite > 0 else None
        return await self._repo.obtener_todos(esquema_norm, limite_norm)

    async def obtener_por_codigo(self, codigo, esquema=None):
        if not codigo or not codigo.strip():
            raise ValueError("El codigo no puede estar vacio.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.obtener_por_codigo(codigo, esquema_norm)

    async def crear(self, datos, esquema=None):
        if not datos:
            raise ValueError("Los datos no pueden estar vacios.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.crear(datos, esquema_norm)

    async def actualizar(self, codigo, datos, esquema=None):
        if not codigo or not codigo.strip():
            raise ValueError("El codigo no puede estar vacio.")
        if not datos:
            raise ValueError("Los datos no pueden estar vacios.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.actualizar(codigo, datos, esquema_norm)

    async def eliminar(self, codigo, esquema=None):
        if not codigo or not codigo.strip():
            raise ValueError("El codigo no puede estar vacio.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.eliminar(codigo, esquema_norm)
```

**8. `servicios/fabrica_repositorios.py`** — Agregar factory de cliente:

```python
# =====================================================================
# FACTORY DE CLIENTE (agregar al final del archivo)
# =====================================================================

from repositorios.cliente import RepositorioClientePostgreSQL    # NUEVO
from servicios.servicio_cliente import ServicioCliente            # NUEVO

_REPOS_CLIENTE = {
    "postgres": RepositorioClientePostgreSQL,
    "postgresql": RepositorioClientePostgreSQL,
}

def crear_servicio_cliente() -> ServicioCliente:
    """Crea el servicio especifico de cliente."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_CLIENTE, proveedor, nombre)
    return ServicioCliente(repo)
```

**9. `controllers/cliente_controller.py`** — Controller (misma estructura que producto):

```python
"""Controller especifico para la tabla cliente."""

from fastapi import APIRouter, HTTPException, Query, Response
from models.cliente import Cliente
from servicios.fabrica_repositorios import crear_servicio_cliente

router = APIRouter(prefix="/api/cliente", tags=["Cliente"])

@router.get("/")
async def listar_clientes(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todos los clientes."""
    try:
        servicio = crear_servicio_cliente()
        filas = await servicio.listar(esquema, limite)
        if len(filas) == 0:
            return Response(status_code=204)
        return {"tabla": "cliente", "total": len(filas), "datos": filas}
    except ValueError as ex:
        raise HTTPException(status_code=400, detail={"estado": 400, "mensaje": str(ex)})
    except Exception as ex:
        raise HTTPException(status_code=500, detail={"estado": 500, "mensaje": str(ex)})

# ... (los otros 4 endpoints siguen la MISMA estructura que producto_controller.py)
```

**10. `main.py`** — Registrar router:

```python
from controllers.cliente_controller import router as cliente_router  # NUEVO

app.include_router(producto_router)
app.include_router(cliente_router)   # <── 1 LINEA NUEVA
```

### 7.6.4 Patron repetible para N entidades

| Paso | Accion | Tiempo estimado |
|------|--------|----------------|
| 1 | Crear modelo Pydantic | 2 minutos |
| 2 | Crear Protocol del repositorio | 3 minutos |
| 3 | Crear repositorio concreto | 3 minutos (copiar y cambiar TABLA/CLAVE) |
| 4 | Crear Protocol del servicio | 3 minutos |
| 5 | Crear servicio | 5 minutos |
| 6 | Agregar factory | 2 minutos |
| 7 | Crear controller | 10 minutos |
| 8 | Registrar router en main.py | 1 minuto |
| **Total** | **1 entidad completa** | **~30 minutos** |

> **Dato**: El proyecto completo original ([ApiFacturasFastApi_Crud](https://github.com/ccastro2050/ApiFacturasFastApi_Crud)) tiene **12 entidades** (producto, cliente, factura, detalle factura, proveedor, etc.), todas siguiendo esta MISMA arquitectura. La consistencia es la clave: una vez que dominas el patron con `producto`, puedes replicarlo mecanicamente para cualquier entidad.

---

## 7.7 Diagrama de arquitectura completa

### 7.7.1 Vista por capas con todos los archivos

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                    CLIENTE HTTP                                          │
│            (Postman / Swagger UI / Frontend)                             │
│                                                                         │
│    GET  /api/producto/          ──> Listar todos                        │
│    GET  /api/producto/{codigo}  ──> Obtener uno                         │
│    POST /api/producto/          ──> Crear                               │
│    PUT  /api/producto/{codigo}  ──> Actualizar                          │
│    DELETE /api/producto/{codigo}──> Eliminar                            │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  PUNTO DE ENTRADA                                                        │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ main.py (77 lineas)                                                │ │
│  │                                                                    │ │
│  │ app = FastAPI(title="API Producto - Tutorial FastAPI")             │ │
│  │ app.include_router(producto_router)                                │ │
│  │ @app.get("/") ──> endpoint raiz de verificacion                   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  CAPA DE PRESENTACION                                                    │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ controllers/producto_controller.py (218 lineas)                    │ │
│  │                                                                    │ │
│  │ router = APIRouter(prefix="/api/producto", tags=["Producto"])      │ │
│  │ 5 funciones async:                                                 │ │
│  │   listar_productos()      ──> GET  /                              │ │
│  │   obtener_producto()      ──> GET  /{codigo}                      │ │
│  │   crear_producto()        ──> POST /                              │ │
│  │   actualizar_producto()   ──> PUT  /{codigo}                      │ │
│  │   eliminar_producto()     ──> DELETE /{codigo}                    │ │
│  │                                                                    │ │
│  │ Manejo de errores: HTTPException 400, 404, 500                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ models/producto.py (26 lineas)                                     │ │
│  │                                                                    │ │
│  │ class Producto(BaseModel):                                         │ │
│  │     codigo: str                                                    │ │
│  │     nombre: str                                                    │ │
│  │     stock: int | None = None                                       │ │
│  │     valorunitario: float | None = None                             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ crear_servicio_producto()
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  CAPA DE NEGOCIO                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ servicios/fabrica_repositorios.py (57 lineas) ──> FACTORY          │ │
│  │                                                                    │ │
│  │ _REPOS_PRODUCTO = {"postgres": RepositorioProductoPostgreSQL}     │ │
│  │ crear_servicio_producto():                                         │ │
│  │   1. _obtener_proveedor() ──> lee DB_PROVIDER                     │ │
│  │   2. _crear_repo_entidad() ──> instancia repositorio              │ │
│  │   3. return ServicioProducto(repo) ──> inyecta dependencia        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ servicios/servicio_producto.py (58 lineas) ──> SERVICE LAYER       │ │
│  │                                                                    │ │
│  │ class ServicioProducto:                                            │ │
│  │   __init__(self, repositorio) ──> DI por constructor              │ │
│  │   listar() ──> normaliza esquema/limite, delega a repo            │ │
│  │   obtener_por_codigo() ──> valida codigo, delega a repo           │ │
│  │   crear() ──> valida datos no vacios, delega a repo               │ │
│  │   actualizar() ──> valida codigo + datos, delega a repo           │ │
│  │   eliminar() ──> valida codigo, delega a repo                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ servicios/conexion/proveedor_conexion.py (56 lineas)               │ │
│  │                                                                    │ │
│  │ class ProveedorConexion:                                           │ │
│  │   proveedor_actual ──> property: "postgres"                       │ │
│  │   obtener_cadena_conexion() ──> "postgresql+asyncpg://..."        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ INTERFACES (Protocols):                                            │ │
│  │   i_proveedor_conexion.py (24 lineas) ──> 1 property + 1 metodo  │ │
│  │   i_servicio_producto.py  (47 lineas) ──> 5 metodos async        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ repo.crear() / repo.obtener_todos() / ...
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  CAPA DE DATOS                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ repositorios/base_repositorio_postgresql.py (373 lineas) ──> BASE  │ │
│  │                                                                    │ │
│  │ class BaseRepositorioPostgreSQL:                                   │ │
│  │   _obtener_engine() ──> lazy loading del pool de conexiones       │ │
│  │   _detectar_tipo_columna() ──> consulta information_schema        │ │
│  │   _convertir_valor() ──> str a int/Decimal/float/UUID/date        │ │
│  │   _serializar_valor() ──> Decimal/date/UUID a JSON                │ │
│  │   _obtener_filas() ──> SELECT * FROM tabla LIMIT n                │ │
│  │   _obtener_por_clave() ──> SELECT * WHERE clave = valor           │ │
│  │   _crear() ──> INSERT INTO tabla VALUES (...)                     │ │
│  │   _actualizar() ──> UPDATE tabla SET ... WHERE ...                │ │
│  │   _eliminar() ──> DELETE FROM tabla WHERE ...                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ repositorios/producto/repositorio_producto_postgresql.py (53 lin.) │ │
│  │                                                                    │ │
│  │ class RepositorioProductoPostgreSQL(BaseRepositorioPostgreSQL):    │ │
│  │   TABLA = "producto"                                               │ │
│  │   CLAVE_PRIMARIA = "codigo"                                        │ │
│  │   obtener_todos() ──> self._obtener_filas(TABLA, ...)             │ │
│  │   obtener_por_codigo() ──> self._obtener_por_clave(TABLA, ...)    │ │
│  │   crear() ──> self._crear(TABLA, ...)                             │ │
│  │   actualizar() ──> self._actualizar(TABLA, ...)                   │ │
│  │   eliminar() ──> self._eliminar(TABLA, ...)                       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ INTERFAZ (Protocol):                                               │ │
│  │   i_repositorio_producto.py (60 lineas) ──> 5 metodos async       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ SQLAlchemy async + asyncpg
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  CONFIGURACION                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ config.py (152 lineas)                                             │ │
│  │   DatabaseSettings ──> lee DB_PROVIDER, DB_POSTGRES               │ │
│  │   Settings ──> debug, environment, database                       │ │
│  │   @lru_cache get_settings() ──> SINGLETON                         │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ .env ──> ENVIRONMENT, DEBUG, DB_PROVIDER, DB_POSTGRES             │ │
│  │ .gitignore ──> venv/, __pycache__/, .env                          │ │
│  │ requirements.txt ──> fastapi, uvicorn, pydantic, sqlalchemy, ...  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  BASE DE DATOS                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ PostgreSQL                                                         │ │
│  │   Servidor: localhost:5432                                         │ │
│  │   Base de datos: bdfacturas_postgres_local                        │ │
│  │   Esquema: public                                                  │ │
│  │   Tabla: producto                                                  │ │
│  │     - codigo: VARCHAR(30)  PK                                      │ │
│  │     - nombre: VARCHAR(100) NOT NULL                                │ │
│  │     - stock: INTEGER NOT NULL                                      │ │
│  │     - valorunitario: NUMERIC(14,2) NOT NULL                        │ │
│  └─────────��──────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.7.2 Flujo de dependencias (quien conoce a quien)

```
main.py
  └── conoce: controllers/producto_controller.py (importa router)
       └── conoce: models/producto.py (importa Producto)
       └── conoce: servicios/fabrica_repositorios.py (importa crear_servicio_producto)
            └── conoce: servicios/servicio_producto.py (importa ServicioProducto)
            └── conoce: servicios/conexion/proveedor_conexion.py (importa ProveedorConexion)
            │    └── conoce: config.py (importa get_settings)
            │         └── conoce: .env (lee variables de entorno)
            └── conoce: repositorios/producto/repositorio_producto_postgresql.py
                 └── conoce: repositorios/base_repositorio_postgresql.py (hereda)
                      └── conoce: servicios/abstracciones/i_proveedor_conexion.py (Protocol)
```

> **Regla de oro**: Las dependencias SIEMPRE fluyen hacia ABAJO (de presentacion a negocio, de negocio a datos). NUNCA hacia arriba. El repositorio JAMAS importa algo del controller. El servicio JAMAS importa algo del controller. Esta es la Dependency Rule de la arquitectura limpia.

---

## 7.8 Resumen final del tutorial

### 7.8.1 Lo que construimos

A lo largo de **7 partes**, construimos desde cero una API REST CRUD completa para la tabla `producto`, siguiendo las mejores practicas de ingenieria de software:

| Parte | Tema | Que aprendimos |
|-------|------|----------------|
| **Parte 1** | Conceptos Fundamentales | SDLC, SOLID, arquitectura de 3 capas, patrones de diseno, prerrequisitos |
| **Parte 2** | Configuracion del Proyecto | git, `.gitignore`, venv, `requirements.txt`, `.env`, `config.py`, estructura de carpetas, PostgreSQL |
| **Parte 3** | Capa de Datos | `IProveedorConexion`, `IRepositorioProducto`, `ProveedorConexion`, `BaseRepositorioPostgreSQL`, `RepositorioProductoPostgreSQL` |
| **Parte 4** | Capa de Negocio | `IServicioProducto`, `ServicioProducto`, `fabrica_repositorios.py` (Factory) |
| **Parte 5** | Capa de Presentacion | Modelo Pydantic `Producto`, `producto_controller.py` con 5 endpoints CRUD |
| **Parte 6** | Punto de Entrada | `main.py`, ejecucion con uvicorn, pruebas en Swagger UI |
| **Parte 7** | Flujo Completo | Flujo de peticiones, mapa de archivos, patrones, SOLID, extensibilidad |

### 7.8.2 El proyecto en numeros

```
┌─────────────────────────────────────────────┐
│         EL PROYECTO EN NUMEROS              │
├─────────────────────────────────────────────┤
│  Archivos Python:          20               │
│  Archivos de configuracion: 3               │
│  Total de archivos:        23               │
│  Lineas de codigo Python:  ~1272            │
│  Patrones de diseno:        8               │
│  Principios SOLID:          5/5             │
│  Endpoints CRUD:            5               │
│  Capas de arquitectura:     3               │
│  Interfaces (Protocols):    3               │
│  Dependencias (pip):        7               │
└─────────────────────────────────────────────┘
```

### 7.8.3 Los 8 patrones implementados

```
1. Repository          ──> Encapsula acceso a datos
2. Factory             ──> Crea objetos segun configuracion
3. Service Layer       ──> Logica de negocio separada
4. Protocol/Interface  ──> Contratos sin implementacion
5. Template Method     ──> Algoritmo base, detalles en subclase
6. Dependency Injection──> Dependencias por constructor
7. Singleton           ──> Configuracion cacheada (@lru_cache)
8. Strategy            ──> Implementaciones intercambiables
```

### 7.8.4 La arquitectura escala

Este tutorial demuestra el patron con **1 entidad** (`producto`). Pero la misma arquitectura escala a **N entidades** sin perder consistencia:

- El proyecto original ([ApiFacturasFastApi_Crud](https://github.com/ccastro2050/ApiFacturasFastApi_Crud)) tiene **12 entidades**: producto, cliente, factura, detalle de factura, proveedor, empleado, entre otras.
- Todas siguen el **MISMO patron** que aprendimos aqui.
- Agregar una entidad nueva toma ~30 minutos siguiendo el proceso mecanico de la seccion 7.6.
- Cambiar de base de datos requiere crear 1 archivo + modificar 3 archivos de configuracion (seccion 7.5).

### 7.8.5 Que sigue

Ahora que dominas la arquitectura, puedes:

1. **Agregar mas entidades** — Sigue el proceso de la seccion 7.6 para agregar `cliente`, `factura`, `proveedor`, etc.
2. **Agregar soporte para otra BD** — Sigue el proceso de la seccion 7.5 para agregar MySQL, SQL Server o MariaDB.
3. **Estudiar el proyecto completo** — Visita el repositorio original con 12 entidades para ver la arquitectura a escala real.
4. **Agregar autenticacion** — Implementar JWT tokens con FastAPI para proteger los endpoints.
5. **Agregar pruebas** — Crear tests unitarios con pytest, aprovechando que las dependencias se inyectan (facil de mockear).
6. **Desplegar en la nube** — Usar Docker + servicios como Railway, Render o AWS para poner la API en produccion.

### 7.8.6 Repositorio del tutorial

El codigo completo de este tutorial esta disponible en GitHub:

**Tutorial (este proyecto):**
- [https://github.com/ccastro2050/apifacturas_fastapi_tutorial](https://github.com/ccastro2050/apifacturas_fastapi_tutorial)

**Proyecto completo (12 entidades):**
- [https://github.com/ccastro2050/ApiFacturasFastApi_Crud](https://github.com/ccastro2050/ApiFacturasFastApi_Crud)

---

### Mensaje final

Si llegaste hasta aqui, completaste un tutorial que cubre los mismos conceptos que se ensenen en cursos de arquitectura de software a nivel profesional. No solo aprendiste a crear una API — aprendiste **POR QUE** se organiza el codigo de esta manera y **COMO** las decisiones de arquitectura facilitan el mantenimiento y la extension del proyecto a largo plazo.

La diferencia entre un programador junior y uno senior no es la cantidad de codigo que escriben, sino la **calidad de las decisiones arquitectonicas** que toman. Ahora tienes las herramientas para tomar esas decisiones.

---

> **Fin del tutorial** — Parte 7 de 7.
