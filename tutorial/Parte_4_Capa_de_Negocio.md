# PARTE 4: Capa de Negocio — Servicio, Interfaz y Fábrica

> En esta parte construimos la **capa intermedia** de la arquitectura: el servicio que contiene la lógica de negocio, su interfaz (contrato) y la fábrica que conecta todas las piezas. Esta capa es el puente entre los endpoints HTTP (Parte 5) y la base de datos (Parte 3).

> **Nota:** Si ya tienes experiencia con el patrón Service Layer y Factory, puedes ir directamente al **Resumen** al final de esta parte.

---

## 4.1 ¿Qué hace la capa de negocio?

La capa de negocio tiene **una sola responsabilidad**: validar datos y orquestar operaciones. No sabe nada de HTTP (eso es del controller) ni de SQL (eso es del repositorio).

```
Controller (HTTP)  →  Servicio (validación/lógica)  →  Repositorio (SQL)
"Recibí un POST"      "¿Los datos son válidos?"         "INSERT INTO..."
```

**¿Por qué no validar directo en el controller?**

| Sin servicio | Con servicio |
|-------------|-------------|
| El controller valida datos, ejecuta lógica y llama al repositorio | El controller solo recibe HTTP y delega al servicio |
| Si cambias la validación, tocas el controller | Si cambias la validación, solo tocas el servicio |
| Si necesitas la misma lógica desde otro lugar (CLI, cron job), la duplicas | Reutilizas el mismo servicio desde cualquier punto de entrada |
| Viola el principio S de SOLID (responsabilidad única) | Cada capa tiene una sola responsabilidad |

---

## 4.2 Interfaz `IServicioProducto` — Contrato del servicio

Define **qué operaciones** debe ofrecer cualquier servicio de producto. Los nombres de los métodos son de **dominio de negocio** (listar, crear, actualizar), no de SQL (SELECT, INSERT, UPDATE).

**Archivo:** `servicios/abstracciones/i_servicio_producto.py`

```python
"""Contrato del servicio específico para producto."""
# ↑ Docstring del módulo: define el contrato que debe cumplir
# cualquier implementación del servicio de producto.

from typing import Protocol, Any, Optional
# ↑ Protocol: para definir la interfaz (tipado estructural).
# Any: tipo comodín (las columnas pueden ser str, int, Decimal, etc.).
# Optional: equivale a "el tipo indicado o None".


class IServicioProducto(Protocol):
    """Contrato del servicio específico para producto."""
    # ↑ Interfaz del servicio. Cualquier clase que tenga estos 5 métodos
    # con estas firmas será reconocida como un IServicioProducto válido.
    #
    # Nota: los nombres de los métodos son de NEGOCIO, no de SQL:
    #   "listar" (no "select_all")
    #   "crear" (no "insert")
    #   "actualizar" (no "update")
    #   "eliminar" (no "delete")

    async def listar(
        self, esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        ...
    # ↑ OPERACIÓN 1: LISTAR todos los productos.
    # esquema: esquema de BD (opcional, default "public").
    # limite: máximo de resultados (opcional).
    # Retorna: lista de diccionarios con los datos de cada producto.

    async def obtener_por_codigo(
        self, codigo: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        ...
    # ↑ OPERACIÓN 2: BUSCAR un producto por su código.
    # codigo: PK del producto (ej: "PR001").
    # Retorna: lista con 0 o 1 elemento.

    async def crear(
        self, datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        ...
    # ↑ OPERACIÓN 3: CREAR un producto nuevo.
    # datos: diccionario con los campos (codigo, nombre, stock, valorunitario).
    # Retorna: True si se creó exitosamente.

    async def actualizar(
        self, codigo: str,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        ...
    # ↑ OPERACIÓN 4: ACTUALIZAR un producto existente.
    # codigo: PK del producto a actualizar.
    # datos: campos a modificar (sin incluir el código).
    # Retorna: número de filas afectadas (0 si no encontró el producto).

    async def eliminar(
        self, codigo: str,
        esquema: Optional[str] = None
    ) -> int:
        ...
    # ↑ OPERACIÓN 5: ELIMINAR un producto.
    # codigo: PK del producto a eliminar.
    # Retorna: número de filas eliminadas (0 si no existía).
```

**Comparación con la interfaz del repositorio:**

| Método servicio | Método repositorio | ¿Diferencia? |
|----------------|-------------------|-------------|
| `listar()` | `obtener_todos()` | Nombre de negocio vs nombre técnico |
| `obtener_por_codigo()` | `obtener_por_codigo()` | Mismo nombre |
| `crear()` | `crear()` | Mismo nombre |
| `actualizar()` | `actualizar()` | Mismo nombre |
| `eliminar()` | `eliminar()` | Mismo nombre |

En este proyecto los nombres son similares porque la lógica de negocio de producto es simple. En proyectos más complejos, el servicio podría tener métodos como `vender_producto()` que internamente llama a `repositorio.actualizar()` + `repositorio_stock.descontar()`.

---

## 4.3 `ServicioProducto` — La implementación con lógica de negocio

Este archivo contiene las **validaciones y normalización** de datos antes de llamar al repositorio. Es la capa que protege al repositorio de datos inválidos.

**Archivo:** `servicios/servicio_producto.py`

```python
"""Servicio específico para la entidad producto."""
# ↑ Docstring del módulo. Este archivo implementa la lógica de negocio
# para la entidad producto: validaciones, normalización de parámetros
# y delegación al repositorio.

from typing import Any
# ↑ Any: tipo comodín. Lo usamos en dict[str, Any] porque los valores
# de las columnas pueden ser de distintos tipos (str, int, Decimal).


class ServicioProducto:
    """Lógica de negocio para producto."""
    # ↑ Esta clase NO hereda de IServicioProducto.
    # Cumple el contrato por tipado estructural (duck typing):
    # tiene los 5 métodos con las firmas correctas → es válido.

    def __init__(self, repositorio):
        if repositorio is None:
            raise ValueError("repositorio no puede ser None.")
        self._repo = repositorio
    # ↑ Constructor.
    # repositorio → recibe el repositorio de producto (cualquier implementación).
    #   No especifica el tipo concreto (RepositorioProductoPostgreSQL).
    #   Podría ser PostgreSQL, MySQL, o un mock para pruebas.
    #   Esto es INVERSIÓN DE DEPENDENCIAS: depende de la abstracción.
    # Validación: si es None, lanza error inmediato (fail fast).
    # self._repo → guarda la referencia como atributo privado.

    async def listar(self, esquema: str | None = None, limite: int | None = None) -> list[dict[str, Any]]:
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        limite_norm = limite if limite and limite > 0 else None
        return await self._repo.obtener_todos(esquema_norm, limite_norm)
    # ↑ OPERACIÓN 1: LISTAR
    #
    # NORMALIZACIÓN DE PARÁMETROS:
    # esquema_norm:
    #   esquema = "  public  " → "public" (strip quita espacios)
    #   esquema = "  " → None (string vacío o solo espacios → None)
    #   esquema = None → None (se queda None)
    #   La condición "esquema and esquema.strip()" verifica:
    #     1. que esquema no sea None (primer "esquema")
    #     2. que después de strip no quede vacío (esquema.strip())
    #
    # limite_norm:
    #   limite = 50 → 50 (número positivo, se mantiene)
    #   limite = 0 → None (cero no es un límite útil)
    #   limite = -5 → None (negativo no tiene sentido)
    #   limite = None → None (se queda None)
    #
    # Luego DELEGA al repositorio: self._repo.obtener_todos()
    # El servicio NO ejecuta SQL — solo valida y delega.

    async def obtener_por_codigo(self, codigo: str, esquema: str | None = None) -> list[dict[str, Any]]:
        if not codigo or not codigo.strip():
            raise ValueError("El código no puede estar vacío.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.obtener_por_codigo(codigo, esquema_norm)
    # ↑ OPERACIÓN 2: BUSCAR POR CÓDIGO
    #
    # VALIDACIÓN DE NEGOCIO:
    #   "not codigo" → True si codigo es None o ""
    #   "not codigo.strip()" → True si codigo es "   " (solo espacios)
    #   Si el código es inválido, lanza ValueError ANTES de llamar al repo.
    #   Esto evita que el repositorio reciba datos basura.
    #
    # NORMALIZACIÓN: esquema se normaliza igual que en listar().
    # DELEGACIÓN: self._repo.obtener_por_codigo(codigo, esquema_norm)

    async def crear(self, datos: dict[str, Any], esquema: str | None = None) -> bool:
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.crear(datos, esquema_norm)
    # ↑ OPERACIÓN 3: CREAR
    #
    # VALIDACIÓN: "not datos" es True si datos es None, {} o está vacío.
    #   No tiene sentido hacer un INSERT sin datos.
    #
    # Nota: la validación de TIPOS (que stock sea int, que valorunitario
    # sea decimal) la hace Pydantic en el controller (Parte 5).
    # El servicio solo valida que los datos no estén vacíos.

    async def actualizar(self, codigo: str, datos: dict[str, Any], esquema: str | None = None) -> int:
        if not codigo or not codigo.strip():
            raise ValueError("El código no puede estar vacío.")
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.actualizar(codigo, datos, esquema_norm)
    # ↑ OPERACIÓN 4: ACTUALIZAR
    #
    # VALIDACIONES:
    #   1. El código no puede ser vacío (¿qué producto actualizar?)
    #   2. Los datos no pueden ser vacíos (¿qué cambiar?)
    # Ambas validaciones protegen al repositorio de operaciones sin sentido.

    async def eliminar(self, codigo: str, esquema: str | None = None) -> int:
        if not codigo or not codigo.strip():
            raise ValueError("El código no puede estar vacío.")
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        return await self._repo.eliminar(codigo, esquema_norm)
    # ↑ OPERACIÓN 5: ELIMINAR
    #
    # VALIDACIÓN: el código no puede ser vacío.
    # DELEGACIÓN: self._repo.eliminar(codigo, esquema_norm)
```

**Resumen de lo que hace cada método del servicio:**

| Método | Valida | Normaliza | Delega a |
|--------|--------|-----------|----------|
| `listar()` | — | esquema, limite | `repo.obtener_todos()` |
| `obtener_por_codigo()` | codigo no vacío | esquema | `repo.obtener_por_codigo()` |
| `crear()` | datos no vacíos | esquema | `repo.crear()` |
| `actualizar()` | codigo y datos no vacíos | esquema | `repo.actualizar()` |
| `eliminar()` | codigo no vacío | esquema | `repo.eliminar()` |

---

## 4.4 `fabrica_repositorios.py` — El patrón Factory

La fábrica es la pieza que **conecta todo**: lee `DB_PROVIDER` del `.env`, crea el repositorio correcto y lo inyecta en el servicio. El controller nunca sabe qué base de datos se está usando.

**¿Por qué una fábrica?**

Sin fábrica, el controller tendría que hacer esto:

```python
# ❌ MAL — El controller conoce la implementación concreta
from repositorios.producto import RepositorioProductoPostgreSQL
from servicios.conexion.proveedor_conexion import ProveedorConexion

proveedor = ProveedorConexion()
repo = RepositorioProductoPostgreSQL(proveedor)  # ← acoplado a PostgreSQL
servicio = ServicioProducto(repo)
```

Con fábrica, el controller hace esto:

```python
# ✅ BIEN — El controller no sabe qué BD se usa
from servicios.fabrica_repositorios import crear_servicio_producto

servicio = crear_servicio_producto()  # ← la fábrica decide todo
```

**Archivo:** `servicios/fabrica_repositorios.py`

```python
"""
fabrica_repositorios.py — Factory centralizada.

Lee DB_PROVIDER del .env y crea el repositorio y servicio correspondientes.
"""
# ↑ Docstring del módulo. Este archivo implementa el patrón FACTORY:
# una función que CREA objetos sin que el código cliente (controller)
# necesite conocer las clases concretas.

from servicios.conexion.proveedor_conexion import ProveedorConexion
# ↑ Importa la clase que lee la configuración de conexión del .env.

from repositorios.producto import RepositorioProductoPostgreSQL
# ↑ Importa el repositorio concreto de producto para PostgreSQL.
# Si en el futuro agregas MySQL, aquí importarías también
# RepositorioProductoMysqlMariaDB.

from servicios.servicio_producto import ServicioProducto
# ↑ Importa el servicio de producto (lógica de negocio).


# =====================================================================
# HELPERS INTERNOS
# =====================================================================

def _obtener_proveedor():
    """Obtiene el proveedor de conexión y su nombre."""
    proveedor = ProveedorConexion()
    return proveedor, proveedor.proveedor_actual
# ↑ Función auxiliar (privada por convención: empieza con _).
# 1. Crea un ProveedorConexion (lee .env vía config.py)
# 2. Retorna una tupla: (objeto_proveedor, "postgres")
# Se usa en todas las fábricas para no repetir este código.


def _crear_repo_entidad(repos_por_proveedor: dict, proveedor, nombre: str):
    """Instancia el repositorio específico según el proveedor activo."""
    clase = repos_por_proveedor.get(nombre)
    if clase is None:
        raise ValueError(
            f"Proveedor '{nombre}' no soportado para esta entidad. "
            f"Opciones: {list(repos_por_proveedor.keys())}"
        )
    return clase(proveedor)
# ↑ Función auxiliar genérica que crea un repositorio.
# repos_por_proveedor: diccionario {"postgres": ClaseRepo, "mysql": ClaseRepo, ...}
# proveedor: objeto ProveedorConexion
# nombre: string del proveedor activo (ej: "postgres")
#
# Flujo:
# 1. Busca la clase en el diccionario: repos_por_proveedor["postgres"]
#    → RepositorioProductoPostgreSQL
# 2. Si no existe, lanza error con las opciones válidas
# 3. Crea una instancia: RepositorioProductoPostgreSQL(proveedor)
#    → Le pasa el proveedor de conexión al constructor


# =====================================================================
# FACTORY DE PRODUCTO
# =====================================================================

_REPOS_PRODUCTO = {
    "postgres": RepositorioProductoPostgreSQL,
    "postgresql": RepositorioProductoPostgreSQL,
}
# ↑ Diccionario que mapea nombre de proveedor → clase de repositorio.
# "postgres" y "postgresql" son aliases: ambos apuntan a la misma clase.
#
# Para agregar soporte MySQL en el futuro, solo agregas:
#   "mysql": RepositorioProductoMysqlMariaDB,
#   "mariadb": RepositorioProductoMysqlMariaDB,
# ¡Sin tocar NADA más! Esto es el principio Open/Closed de SOLID.
#
# NOTA: En el proyecto completo (ApiFacturasFastApi_Crud), este diccionario
# también incluye sqlserver, sqlserverexpress, localdb, mysql, mariadb.


def crear_servicio_producto() -> ServicioProducto:
    """Crea el servicio específico de producto."""
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_PRODUCTO, proveedor, nombre)
    return ServicioProducto(repo)
# ↑ LA FUNCIÓN QUE USA EL CONTROLLER.
# Es la ÚNICA función pública de este archivo para producto.
#
# Flujo completo:
# 1. _obtener_proveedor()
#    → ProveedorConexion() lee .env → DB_PROVIDER = "postgres"
#    → Retorna: (proveedor_obj, "postgres")
#
# 2. _crear_repo_entidad(_REPOS_PRODUCTO, proveedor_obj, "postgres")
#    → Busca en el diccionario: _REPOS_PRODUCTO["postgres"]
#    → Obtiene: RepositorioProductoPostgreSQL
#    → Crea: RepositorioProductoPostgreSQL(proveedor_obj)
#    → Retorna: instancia del repositorio
#
# 3. ServicioProducto(repo)
#    → Crea el servicio inyectándole el repositorio
#    → El servicio no sabe si el repo es PostgreSQL, MySQL o un mock
#
# 4. Retorna el servicio listo para usar.
#
# El controller solo hace:
#   servicio = crear_servicio_producto()
#   datos = await servicio.listar()
```

### Diagrama del flujo de creación

```
crear_servicio_producto()
│
├── 1. _obtener_proveedor()
│       ├── ProveedorConexion()
│       │   └── get_settings()          ← lee .env (singleton)
│       └── proveedor.proveedor_actual  ← "postgres"
│
├── 2. _crear_repo_entidad()
│       ├── _REPOS_PRODUCTO["postgres"]
│       │   └── RepositorioProductoPostgreSQL  ← clase (no instancia)
│       └── RepositorioProductoPostgreSQL(proveedor)  ← crea instancia
│
└── 3. ServicioProducto(repo)           ← inyecta el repositorio
        └── self._repo = repo           ← guardado para usar en los 5 métodos
```

---

## 4.5 ¿Cómo se conectan las 3 capas?

Ahora que tenemos las 3 capas de lógica completas, veamos cómo se ensamblan:

```
┌──────────────────────────────────────────────────────┐
│  Controller (Parte 5)                                │
│  producto_controller.py                              │
│                                                      │
│  servicio = crear_servicio_producto()   ← Fábrica    │
│  datos = await servicio.listar()        ← Servicio   │
└──────────────────┬───────────────────────────────────┘
                   │ llama a
┌──────────────────▼───────────────────────────────────┐
│  Servicio (esta Parte)                               │
│  servicio_producto.py                                │
│                                                      │
│  esquema_norm = esquema.strip() ...    ← Normaliza   │
│  return await self._repo.obtener_todos() ← Delega   │
└──────────────────┬───────────────────────────────────┘
                   │ llama a
┌──────────────────▼───────────────────────────────────┐
│  Repositorio (Parte 3)                               │
│  repositorio_producto_postgresql.py                  │
│  → base_repositorio_postgresql.py                    │
│                                                      │
│  SELECT * FROM "public"."producto" LIMIT :limite     │
└──────────────────┬───────────────────────────────────┘
                   │ ejecuta SQL
              ┌────▼────┐
              │PostgreSQL│
              └─────────┘
```

**Principio clave: cada capa solo conoce a la capa inmediatamente inferior.**
- El controller conoce al servicio (pero no al repositorio)
- El servicio conoce al repositorio (pero no al SQL)
- El repositorio conoce al SQL (pero no al HTTP)

---

## Resumen de la Parte 4

### Archivos creados

| # | Archivo | Capa | Líneas | Propósito |
|---|---------|------|--------|-----------|
| 1 | `servicios/abstracciones/i_servicio_producto.py` | Abstracción | 39 | Contrato: 5 operaciones de negocio |
| 2 | `servicios/servicio_producto.py` | Negocio | 44 | Validaciones, normalización, delegación al repo |
| 3 | `servicios/fabrica_repositorios.py` | Negocio | ~45 | Factory: lee .env, crea repo, inyecta en servicio |

### Patrones aplicados en esta parte

| Patrón | Dónde | Qué resuelve |
|--------|-------|-------------|
| **Service Layer** | `ServicioProducto` | Separa lógica de negocio del HTTP y del SQL |
| **Factory** | `fabrica_repositorios.py` | Crea los objetos correctos según configuración |
| **Dependency Injection** | `ServicioProducto(repo)` | El servicio recibe el repo sin saber cuál es |
| **Strategy** | `_REPOS_PRODUCTO` dict | Cambia la implementación cambiando `.env` |
| **Protocol (Interface)** | `IServicioProducto` | Contrato del servicio sin herencia obligatoria |

### Referencia rápida — ¿Quién llama a quién?

| Capa | Archivo | Llama a | Método |
|------|---------|---------|--------|
| Controller | `producto_controller.py` | `crear_servicio_producto()` | Factory |
| Factory | `fabrica_repositorios.py` | `ServicioProducto(repo)` | Constructor |
| Servicio | `servicio_producto.py` | `self._repo.obtener_todos()` | Repositorio |
| Repositorio | `repositorio_producto_postgresql.py` | `self._obtener_filas("producto")` | Clase base |
| Clase base | `base_repositorio_postgresql.py` | `engine.connect()` + SQL | PostgreSQL |

---

## Siguiente paso

En la **Parte 5** construiremos la **capa de presentación**: el modelo Pydantic `Producto` (validación de datos de entrada) y el controller `producto_controller.py` (los 5 endpoints HTTP). Es la capa que el cliente HTTP ve directamente.

---

> **Nota:** Al terminar esta parte, tienes las 3 capas de lógica completas (datos, negocio, presentación parcial). Solo faltan el modelo Pydantic, el controller y el `main.py` para poder ejecutar la API.
