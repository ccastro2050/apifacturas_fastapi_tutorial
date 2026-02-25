# PARTE 1: Conceptos Fundamentales

## Tutorial: API REST CRUD de Productos con Python y FastAPI

> **Proyecto:** `apifacturas_fastapi_tutorial`
> **Entidad:** Tabla `producto` (PostgreSQL)
> **Arquitectura:** 3 capas con patrones de diseño empresariales

---

## 1.1 SDLC — Ciclo de Vida del Desarrollo de Software

Antes de escribir una sola línea de código, todo proyecto de software profesional sigue un **ciclo de vida** (SDLC — Software Development Life Cycle). Esto garantiza que el desarrollo sea ordenado, predecible y mantenible.

| # | Fase | Descripción | En este proyecto |
|---|------|-------------|------------------|
| 1 | **Análisis** | Definir qué se necesita construir | API REST CRUD para gestionar productos en PostgreSQL |
| 2 | **Diseño** | Definir cómo se va a construir (arquitectura, patrones, tecnologías) | Arquitectura 3 capas + 8 patrones de diseño + FastAPI + SQLAlchemy async |
| 3 | **Desarrollo** | Escribir el código fuente | Este tutorial (Partes 2 a 6) |
| 4 | **Pruebas** | Verificar que funciona correctamente | Probar los 5 endpoints con Swagger UI (Parte 6) |
| 5 | **Despliegue** | Poner en producción | `uvicorn main:app` en un servidor |
| 6 | **Mantenimiento** | Corregir errores, agregar mejoras | Agregar soporte para MySQL, nuevas entidades, etc. |

**¿Por qué importa esto?** Porque muchos desarrolladores saltan directo a programar sin analizar ni diseñar. El resultado: código desordenado, difícil de mantener, difícil de escalar. En este tutorial, las Partes 1 y 2 cubren el análisis y diseño antes de tocar código de la API.

---

## 1.2 Principios SOLID

SOLID es un conjunto de 5 principios de diseño orientado a objetos que guían la construcción de software profesional. Cada letra representa un principio. Aquí los explicamos con **ejemplos concretos de este proyecto**.

### S — Single Responsibility Principle (Responsabilidad Única)

> **"Cada clase debe tener una sola razón para cambiar."**

Cada archivo de este proyecto tiene **una sola responsabilidad**:

| Archivo | Responsabilidad única | Si cambia... |
|---------|----------------------|--------------|
| `producto_controller.py` | Recibir peticiones HTTP y devolver respuestas JSON | Solo se modifica si cambian los endpoints (URLs, parámetros) |
| `servicio_producto.py` | Validar datos y aplicar reglas de negocio | Solo se modifica si cambian las validaciones |
| `repositorio_producto_postgresql.py` | Ejecutar SQL contra PostgreSQL | Solo se modifica si cambia la estructura de la tabla |
| `config.py` | Leer configuración desde `.env` | Solo se modifica si se agregan nuevas variables de entorno |

**Contraejemplo (MAL diseño):** Un solo archivo `app.py` de 500 líneas que recibe HTTP, valida datos, construye SQL y se conecta a la base de datos. Si cambias la base de datos, tocas el mismo archivo donde están los endpoints. Si cambias una validación, tocas el mismo archivo donde está el SQL.

---

### O — Open/Closed Principle (Abierto/Cerrado)

> **"Las clases deben estar abiertas para extensión, pero cerradas para modificación."**

**Ejemplo concreto:** Hoy el proyecto usa PostgreSQL. Mañana necesitas agregar soporte para MySQL. ¿Qué archivos modificas?

| Acción | Archivo | ¿Se modifica? |
|--------|---------|--------------|
| Crear `base_repositorio_mysql.py` | **NUEVO** | No existe todavía |
| Crear `repositorio_producto_mysql.py` | **NUEVO** | No existe todavía |
| Agregar entrada en `fabrica_repositorios.py` | Se agregan **2 líneas** al diccionario | Mínimo cambio |
| Agregar `DB_MYSQL=...` en `.env` | Se agrega **1 línea** | Configuración, no código |
| `producto_controller.py` | **NO se toca** | Cerrado para modificación |
| `servicio_producto.py` | **NO se toca** | Cerrado para modificación |
| `models/producto.py` | **NO se toca** | Cerrado para modificación |

**Resultado:** El controller, el servicio y el modelo están **cerrados** (no se tocan). El sistema está **abierto** a agregar nuevos motores de base de datos sin romper nada existente.

---

### L — Liskov Substitution Principle (Sustitución de Liskov)

> **"Si una clase B hereda de A, entonces B debe poder usarse en cualquier lugar donde se use A sin que el programa falle."**

**Ejemplo concreto:** Cambia `DB_PROVIDER=postgres` a `DB_PROVIDER=mysql` en el `.env`. La API sigue funcionando exactamente igual porque:

- `RepositorioProductoPostgreSQL` cumple el contrato `IRepositorioProducto`
- `RepositorioProductoMysqlMariaDB` cumple el **mismo** contrato `IRepositorioProducto`
- El `ServicioProducto` no sabe (ni le importa) cuál repositorio tiene adentro

Son **intercambiables**. Cualquiera puede sustituir al otro sin que nada se rompa. Eso es Liskov.

---

### I — Interface Segregation Principle (Segregación de Interfaces)

> **"Es mejor tener muchas interfaces pequeñas y específicas que una interfaz grande y genérica."**

**Ejemplo concreto:** En este proyecto tenemos interfaces (Protocols) pequeñas y enfocadas:

| Interface (Protocol) | Métodos | Responsabilidad |
|---------------------|---------|----------------|
| `IRepositorioProducto` | 5 métodos: `obtener_todos`, `obtener_por_codigo`, `crear`, `actualizar`, `eliminar` | Solo operaciones CRUD de producto |
| `IServicioProducto` | 5 métodos: `listar`, `obtener_por_codigo`, `crear`, `actualizar`, `eliminar` | Solo lógica de negocio de producto |
| `IProveedorConexion` | 2 miembros: `proveedor_actual` (propiedad), `obtener_cadena_conexion` (método) | Solo entregar la conexión a BD |

**Contraejemplo (MAL diseño):** Una sola interfaz `IRepositorioGenerico` con 20 métodos que incluye operaciones de producto, factura, usuario, login, reportes... Cada repositorio estaría obligado a implementar métodos que no necesita.

---

### D — Dependency Inversion Principle (Inversión de Dependencias)

> **"Las clases de alto nivel no deben depender de clases de bajo nivel. Ambas deben depender de abstracciones."**

**Ejemplo concreto:**

```
                    ┌─────────────────────────┐
                    │    ServicioProducto      │  ← Clase de ALTO nivel
                    │                         │
                    │  Depende de:            │
                    │  IRepositorioProducto   │  ← ABSTRACCIÓN (Protocol)
                    │  (NO de PostgreSQL)     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
          ┌─────────────────┐     ┌─────────────────────┐
          │ RepoProducto    │     │ RepoProducto        │
          │ PostgreSQL      │     │ MySQL               │
          │ (bajo nivel)    │     │ (bajo nivel)        │
          └─────────────────┘     └─────────────────────┘
```

`ServicioProducto` **nunca** importa `RepositorioProductoPostgreSQL`. Ni siquiera sabe que existe. Solo sabe que recibe un objeto que cumple con `IRepositorioProducto`. La **fábrica** (`fabrica_repositorios.py`) es quien decide qué clase concreta inyectar.

**En .NET equivale a:**
```csharp
// ASP.NET — El servicio depende de la interfaz, no del concreto
services.AddScoped<IRepositorioProducto, RepositorioProductoPostgreSQL>();
```

**En Python lo hacemos con la fábrica:**
```python
# fabrica_repositorios.py — La fábrica inyecta el repositorio correcto
def crear_servicio_producto():
    repo = RepositorioProductoPostgreSQL(proveedor)  # Decisión aquí
    return ServicioProducto(repo)                     # Inyección aquí
```

---

## 1.3 Arquitectura de 3 Capas

Este proyecto separa el código en **3 capas**, cada una con una responsabilidad clara. Las peticiones fluyen de arriba hacia abajo, y las respuestas de abajo hacia arriba.

```
    ┌──────────────────────────────────────────────────────────────────────┐
    │                        CLIENTE (Postman / Navegador / Frontend)     │
    └──────────────────────────────┬───────────────────────────────────────┘
                                   │  HTTP Request (GET, POST, PUT, DELETE)
                                   ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │  CAPA 1: PRESENTACIÓN (Controllers)                                 │
    │                                                                      │
    │  producto_controller.py                                              │
    │  - Recibe la petición HTTP                                           │
    │  - Extrae parámetros (path, query, body)                            │
    │  - Llama al servicio                                                │
    │  - Devuelve JSON con código de estado (200, 404, 500)               │
    └──────────────────────────────┬───────────────────────────────────────┘
                                   │  Llama a servicio.listar(), .crear(), etc.
                                   ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │  CAPA 2: NEGOCIO (Services)                                         │
    │                                                                      │
    │  servicio_producto.py                                                │
    │  - Valida datos de entrada (código vacío, datos nulos)              │
    │  - Normaliza parámetros (esquema, límite)                           │
    │  - Delega al repositorio                                            │
    │  - NO sabe de HTTP, NO sabe de SQL                                  │
    └──────────────────────────────┬───────────────────────────────────────┘
                                   │  Llama a repo.obtener_todos(), .crear(), etc.
                                   ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │  CAPA 3: DATOS (Repositories)                                       │
    │                                                                      │
    │  repositorio_producto_postgresql.py                                  │
    │  (hereda de base_repositorio_postgresql.py)                         │
    │  - Construye SQL parametrizado                                       │
    │  - Ejecuta queries con SQLAlchemy async                             │
    │  - Convierte tipos (str → int, Decimal → float)                    │
    │  - Serializa resultados a dict                                      │
    │  - NO sabe de HTTP, NO sabe de validaciones de negocio              │
    └──────────────────────────────┬───────────────────────────────────────┘
                                   │  SQL (SELECT, INSERT, UPDATE, DELETE)
                                   ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │  BASE DE DATOS: PostgreSQL                                           │
    │                                                                      │
    │  Tabla: producto                                                     │
    │  Columnas: codigo (PK), nombre, stock, valorunitario                │
    └──────────────────────────────────────────────────────────────────────┘
```

### ¿Por qué 3 capas?

| Beneficio | Explicación |
|-----------|-------------|
| **Separación de responsabilidades** | Cada capa hace una sola cosa. Si hay un bug en el SQL, solo miras el repositorio. Si el JSON sale mal, solo miras el controller. |
| **Testeo independiente** | Puedes probar el servicio con un repositorio falso (mock), sin necesitar una base de datos real. |
| **Cambio de tecnología** | Cambiar de PostgreSQL a MySQL solo afecta la capa de datos. Las capas de negocio y presentación no se enteran. |
| **Trabajo en equipo** | Un desarrollador puede trabajar en el controller mientras otro trabaja en el repositorio, sin interferirse. |

---

## 1.4 Estructura de Carpetas del Proyecto

Al terminar el tutorial, el proyecto tendrá esta estructura. Cada archivo tiene un propósito claro dentro de su capa:

```
apifacturas_fastapi_tutorial/
│
├── main.py                          ← Punto de entrada. Registra el router y arranca FastAPI
├── config.py                        ← Lee configuración desde .env (Singleton con @lru_cache)
├── requirements.txt                 ← Dependencias del proyecto (pip install -r)
├── .env                             ← Variables de entorno (DB_PROVIDER, cadenas de conexión)
├── .gitignore                       ← Archivos que Git debe ignorar (venv/, .env, __pycache__/)
│
├── models/                          ← MODELOS PYDANTIC (validación de datos de entrada)
│   ├── __init__.py
│   └── producto.py                  ← Clase Producto con 4 campos validados
│
├── controllers/                     ← CAPA 1: PRESENTACIÓN (endpoints HTTP)
│   ├── __init__.py
│   └── producto_controller.py       ← 5 endpoints: GET, GET/{id}, POST, PUT, DELETE
│
├── servicios/                       ← CAPA 2: NEGOCIO (lógica y validaciones)
│   ├── __init__.py
│   ├── servicio_producto.py         ← Valida inputs, normaliza parámetros, delega al repo
│   ├── fabrica_repositorios.py      ← Factory: crea repo + servicio según DB_PROVIDER
│   ├── abstracciones/               ← Interfaces (Protocols) de la capa de negocio
│   │   ├── __init__.py
│   │   ├── i_proveedor_conexion.py  ← Contrato para proveedores de conexión
│   │   └── i_servicio_producto.py   ← Contrato del servicio de producto
│   └── conexion/                    ← Proveedor de conexión a base de datos
│       ├── __init__.py
│       └── proveedor_conexion.py    ← Lee DB_PROVIDER y retorna la cadena de conexión
│
├── repositorios/                    ← CAPA 3: DATOS (acceso a base de datos)
│   ├── __init__.py
│   ├── base_repositorio_postgresql.py  ← Clase base con lógica SQL reutilizable (~380 líneas)
│   ├── abstracciones/               ← Interfaces (Protocols) de la capa de datos
│   │   ├── __init__.py
│   │   └── i_repositorio_producto.py  ← Contrato del repositorio de producto (5 métodos)
│   └── producto/                    ← Repositorio específico de producto
│       ├── __init__.py
│       └── repositorio_producto_postgresql.py  ← Implementación para PostgreSQL (~37 líneas)
│
└── database/                        ← Scripts SQL
    └── producto_postgres.sql        ← CREATE TABLE + datos de ejemplo
```

**Total de archivos de código: 18** (sin contar `__init__.py` vacíos)

---

## 1.5 Patrones de Diseño Utilizados

Este proyecto implementa **8 patrones de diseño**. Cada uno resuelve un problema concreto.

| # | Patrón | Archivo(s) donde se aplica | Qué problema resuelve | Equivalencia en .NET / C# |
|---|--------|---------------------------|----------------------|---------------------------|
| 1 | **Repository** | `repositorio_producto_postgresql.py` | Abstrae el acceso a datos detrás de una interfaz. El servicio no sabe si habla con PostgreSQL, MySQL o un archivo JSON | `IRepository<Producto>` |
| 2 | **Factory** | `fabrica_repositorios.py` | Centraliza la creación de objetos. Lee `DB_PROVIDER` y decide qué repositorio crear, sin que el controller lo sepa | `IServiceCollection.AddScoped<>()` |
| 3 | **Service Layer** | `servicio_producto.py` | Separa la lógica de negocio (validaciones) de la capa HTTP y la capa SQL | `ProductoService` en la capa de aplicación |
| 4 | **Protocol (Interface)** | `i_repositorio_producto.py`, `i_servicio_producto.py`, `i_proveedor_conexion.py` | Define contratos que las clases deben cumplir, sin acoplamiento directo. Usa **tipado estructural** (duck typing tipado) | `interface IRepositorioProducto` |
| 5 | **Template Method** | `base_repositorio_postgresql.py` → `repositorio_producto_postgresql.py` | La clase base define el algoritmo (construir SQL, ejecutar, serializar). La subclase solo configura `TABLA` y `CLAVE_PRIMARIA` | `abstract class BaseRepository<T>` con métodos virtuales |
| 6 | **Dependency Injection** | `ServicioProducto.__init__(self, repositorio)` | El servicio recibe su dependencia desde afuera (la fábrica), en vez de crearla internamente | Constructor injection en ASP.NET |
| 7 | **Singleton** | `config.py` → `@lru_cache()` en `get_settings()` | La configuración se lee del `.env` una sola vez y se reutiliza en toda la aplicación | `services.AddSingleton<Settings>()` |
| 8 | **Strategy** | Diccionario `_REPOS_PRODUCTO` en `fabrica_repositorios.py` | Diferentes implementaciones (PostgreSQL, MySQL, SQL Server) son estrategias intercambiables para resolver el mismo problema | `Dictionary<string, Type>` con resolución en runtime |

---

## 1.6 Prerequisitos

Antes de comenzar, asegúrate de tener instalado:

| Herramienta | Versión mínima | ¿Para qué? | Cómo verificar |
|-------------|---------------|-------------|----------------|
| **Python** | 3.11+ | Lenguaje del proyecto. Necesita 3.11+ por la sintaxis `str \| None` | `python --version` |
| **PostgreSQL** | 12+ | Base de datos donde se almacenan los productos | `psql --version` |
| **pip** | 21+ | Instalador de paquetes Python | `pip --version` |
| **Git** | 2.30+ | Control de versiones | `git --version` |
| **VS Code** | Último | Editor recomendado (con extensión Python) | Abrir VS Code |
| **Postman** (opcional) | Último | Cliente HTTP para probar la API. Alternativa: usar Swagger UI integrado | Abrir Postman |

---

## 1.7 Flujo Completo de una Petición (Recorrido Conceptual)

Antes de escribir código, recorramos **paso a paso** qué sucede cuando un cliente hace una petición. Ejemplo: `GET /api/producto/PR001`

```
PASO 1 → El cliente (Postman/navegador) envía:
          GET http://localhost:8000/api/producto/PR001

PASO 2 → FastAPI (en main.py) recibe la petición y busca qué router
          tiene registrada la ruta /api/producto/{codigo}.
          La encuentra en producto_controller.py (prefix="/api/producto").

PASO 3 → producto_controller.py ejecuta la función obtener_producto("PR001").
          Internamente hace:
            servicio = crear_servicio_producto()   ← Llama a la fábrica

PASO 4 → fabrica_repositorios.py (la fábrica) hace:
            a) Lee DB_PROVIDER del .env → "postgres"
            b) Busca en _REPOS_PRODUCTO["postgres"] → RepositorioProductoPostgreSQL
            c) Crea: repo = RepositorioProductoPostgreSQL(proveedor)
            d) Crea: servicio = ServicioProducto(repo)   ← Inyección de dependencia
            e) Retorna el servicio al controller

PASO 5 → El controller llama:
            filas = await servicio.obtener_por_codigo("PR001")

PASO 6 → ServicioProducto.obtener_por_codigo("PR001") hace:
            a) Valida que "PR001" no esté vacío → OK
            b) Normaliza el esquema (None → None)
            c) Delega: return await self._repo.obtener_por_codigo("PR001", None)

PASO 7 → RepositorioProductoPostgreSQL.obtener_por_codigo("PR001") hace:
            return await self._obtener_por_clave("producto", "codigo", "PR001")
            (Llama al método protegido de la clase base)

PASO 8 → BaseRepositorioPostgreSQL._obtener_por_clave() hace:
            a) Esquema por defecto → "public"
            b) Consulta information_schema para detectar el tipo de "codigo" → VARCHAR
            c) Construye SQL: SELECT * FROM "public"."producto" WHERE "codigo" = :valor
            d) Ejecuta el SQL con SQLAlchemy async, pasando {"valor": "PR001"}
            e) Recibe la fila: ('PR001', 'Laptop Lenovo IdeaPad', 20, 2500000.00)
            f) Serializa a dict: {"codigo": "PR001", "nombre": "Laptop Lenovo IdeaPad",
                                   "stock": 20, "valorunitario": 2500000.0}
            g) Retorna [{"codigo": "PR001", ...}]

PASO 9 → La respuesta sube de vuelta:
            Repo → Servicio → Controller

PASO 10 → El controller construye la respuesta JSON:
            {
                "tabla": "producto",
                "total": 1,
                "datos": [
                    {
                        "codigo": "PR001",
                        "nombre": "Laptop Lenovo IdeaPad",
                        "stock": 20,
                        "valorunitario": 2500000.0
                    }
                ]
            }
          FastAPI la envía al cliente con HTTP 200 OK.
```

### Resumen visual del flujo:

```
Cliente HTTP
    │
    ▼
producto_controller.py ──→ crear_servicio_producto() ──→ fabrica_repositorios.py
    │                                                          │
    │                                                    Lee DB_PROVIDER
    │                                                    Crea Repo + Servicio
    │                                                          │
    ▼                                                          ▼
servicio.obtener_por_codigo("PR001")              ServicioProducto(repo)
    │
    ▼
Valida "PR001" → OK
Delega a repo.obtener_por_codigo("PR001")
    │
    ▼
RepositorioProductoPostgreSQL
    → self._obtener_por_clave("producto", "codigo", "PR001")
    │
    ▼
BaseRepositorioPostgreSQL
    → SELECT * FROM "public"."producto" WHERE "codigo" = 'PR001'
    │
    ▼
PostgreSQL → Retorna fila → Serializa a dict → Sube por las capas → JSON al cliente
```

---

## Siguiente paso

En la **Parte 2** crearemos el proyecto desde cero: directorio, Git, credenciales de GitHub, entorno virtual, dependencias, configuración y la base de datos PostgreSQL.

---

> **Nota:** Este tutorial forma parte del proyecto `apifacturas_fastapi_tutorial`. Cada parte se construye sobre la anterior. Al final tendrás una API REST completamente funcional con arquitectura profesional.
