# PARTE 3: Capa de Datos — Interfaces, Conexión y Repositorios

> En esta parte construimos la **capa más baja** de la arquitectura: todo lo que se comunica directamente con la base de datos. Creamos las interfaces (contratos), el proveedor de conexión, el repositorio base con la lógica SQL genérica (~350 líneas) y el repositorio específico de producto.

> **Nota:** Si ya tienes experiencia con SQLAlchemy async y el patrón Repository, puedes ir directamente al **Resumen** al final de esta parte.

---

## 3.1 ¿Qué es una interfaz en Python? — `Protocol` vs `ABC`

Antes de escribir código, entendamos **qué es una interfaz** y cómo se implementa en Python.

Una **interfaz** es un contrato: define **qué métodos debe tener** una clase, pero **no cómo los implementa**. Es como un plano que dice "toda clase que cumpla este contrato debe tener estos métodos con estas firmas".

### ¿Por qué usar interfaces?

| Sin interfaz | Con interfaz |
|-------------|-------------|
| El servicio depende directamente de `RepositorioProductoPostgreSQL` | El servicio depende del **contrato** `IRepositorioProducto` |
| Si cambias de PostgreSQL a MySQL, debes modificar el servicio | Si cambias de PostgreSQL a MySQL, el servicio no se entera |
| Acoplamiento fuerte (viola el principio D de SOLID) | Acoplamiento débil (cumple Inversión de Dependencias) |

### Python tiene dos formas de definir interfaces:

| Mecanismo | Módulo | Tipo de tipado | Cómo funciona |
|-----------|--------|----------------|---------------|
| `ABC` (Abstract Base Class) | `abc` | **Nominal** — la clase debe heredar explícitamente | Si la clase no hereda de la ABC, Python no la reconoce como implementación aunque tenga los mismos métodos |
| `Protocol` | `typing` | **Estructural** (duck typing) — si tiene los métodos, cumple | Si la clase tiene los métodos con las firmas correctas, Python la acepta automáticamente. No necesita heredar de nada |

### En este proyecto usamos `Protocol` porque:

1. **No obliga a heredar** — la clase solo necesita tener los métodos correctos
2. **Es más flexible** — puedes cambiar la implementación sin tocar la interfaz
3. **Duck typing** — "si camina como pato y grazna como pato, es un pato"
4. **Equivalente a interfaces en C#/Java** — define contratos sin implementación

### Equivalencias con otros lenguajes:

| Python (`Protocol`) | C# | Java |
|--------------------|-----|------|
| `class IRepositorioProducto(Protocol):` | `interface IRepositorioProducto` | `interface IRepositorioProducto` |
| No necesita `implements` | `class Repo : IRepositorioProducto` | `class Repo implements IRepositorioProducto` |
| Cumple si tiene los métodos | Debe declarar que implementa la interfaz | Debe declarar que implementa la interfaz |

---

## 3.2 Interfaz `IProveedorConexion` — Contrato de conexión

Este archivo define **qué debe saber hacer** cualquier clase que provea conexiones a base de datos. No dice **cómo** lo hace — solo dice "debes tener estas capacidades".

**Archivo:** `servicios/abstracciones/i_proveedor_conexion.py`

```python
"""Contrato para obtener información de conexión a BD."""
# ↑ Docstring del módulo: describe el propósito del archivo.
# Python lo usa como documentación cuando haces help() sobre el módulo.

from typing import Protocol
# ↑ Importamos Protocol del módulo typing (tipos de Python).
# Protocol es la clase base para definir interfaces estructurales.
# Una clase que tenga los mismos métodos que este Protocol
# será reconocida automáticamente como implementación válida,
# sin necesidad de heredar explícitamente.


class IProveedorConexion(Protocol):
    """Contrato para clases que proveen información de conexión."""
    # ↑ La "I" al inicio es convención: indica que es una Interface.
    # Heredar de Protocol convierte esta clase en una interfaz estructural.
    # NINGUNA clase necesita escribir "class X(IProveedorConexion)" para cumplir.
    # Solo necesita tener los mismos métodos con las mismas firmas.

    @property
    def proveedor_actual(self) -> str:
        """Nombre del proveedor activo (ej: 'postgres')."""
        ...
    # ↑ @property define un método que se accede como atributo:
    #   proveedor.proveedor_actual  (sin paréntesis, como un campo)
    # → str: debe retornar un string con el nombre del proveedor.
    # Los "..." (Ellipsis) significan "sin implementación" — es solo la firma.

    def obtener_cadena_conexion(self) -> str:
        """Cadena de conexión del proveedor activo."""
        ...
    # ↑ Método que retorna la cadena de conexión completa.
    # Ejemplo: "postgresql+asyncpg://postgres:postgres@localhost:5432/bdfacturas"
    # Los "..." indican que este método no tiene cuerpo aquí.
    # La clase que implemente este contrato definirá el cuerpo.
```

**Este Protocol define 2 capacidades:**

| Miembro | Tipo | Qué debe retornar | Ejemplo |
|---------|------|--------------------|---------|
| `proveedor_actual` | `@property` → `str` | Nombre del motor activo | `"postgres"` |
| `obtener_cadena_conexion()` | método → `str` | Cadena de conexión completa | `"postgresql+asyncpg://..."` |

---

## 3.3 Interfaz `IRepositorioProducto` — Contrato CRUD

Este archivo define **las 5 operaciones** que cualquier repositorio de producto debe implementar: listar, buscar por código, crear, actualizar y eliminar.

**Archivo:** `repositorios/abstracciones/i_repositorio_producto.py`

```python
"""Contrato del repositorio específico para producto."""
# ↑ Docstring del módulo: este archivo define el contrato (interfaz)
# que debe cumplir cualquier repositorio que maneje la tabla producto.

from typing import Protocol, Any, Optional
# ↑ Protocol: para definir la interfaz (tipado estructural).
# Any: tipo comodín — acepta cualquier tipo de dato.
#   Lo usamos en dict[str, Any] porque las columnas pueden ser
#   str, int, Decimal, etc.
# Optional: equivale a "puede ser el tipo indicado o None".
#   Optional[str] es lo mismo que str | None.
#   Lo usamos porque el esquema es opcional (si no lo envían, usa "public").


class IRepositorioProducto(Protocol):
    """Contrato para el repositorio de producto."""
    # ↑ Cualquier clase que tenga estos 5 métodos con estas firmas
    # será reconocida como un IRepositorioProducto válido.
    # No necesita escribir "class X(IRepositorioProducto)".

    async def obtener_todos(
        self,
        esquema: Optional[str] = None,
        limite: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Obtiene todos los productos."""
        ...
    # ↑ OPERACIÓN 1: LISTAR
    # async def → es una función asíncrona (se llama con await).
    # esquema: Optional[str] = None → esquema de BD (opcional, default None → usa "public").
    # limite: Optional[int] = None → máximo de filas (opcional, default None → sin límite fijo).
    # Retorna: list[dict[str, Any]] → lista de diccionarios.
    #   Ejemplo: [{"codigo": "PR001", "nombre": "Laptop", "stock": 20, "valorunitario": 2500000.00}]

    async def obtener_por_codigo(
        self,
        codigo: str,
        esquema: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Obtiene un producto por su código."""
        ...
    # ↑ OPERACIÓN 2: BUSCAR POR CÓDIGO
    # codigo: str → valor de la PK a buscar (ej: "PR001").
    # Retorna lista porque la interfaz es genérica.
    #   Si encuentra: [{"codigo": "PR001", ...}] (1 elemento).
    #   Si no encuentra: [] (lista vacía).

    async def crear(
        self,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> bool:
        """Crea un nuevo producto. Retorna True si se creó."""
        ...
    # ↑ OPERACIÓN 3: CREAR (INSERT)
    # datos: dict[str, Any] → diccionario con los campos del producto.
    #   Ejemplo: {"codigo": "PR006", "nombre": "Mouse", "stock": 10, "valorunitario": 50000}
    # Retorna: bool → True si el INSERT afectó al menos 1 fila, False si no.

    async def actualizar(
        self,
        codigo: str,
        datos: dict[str, Any],
        esquema: Optional[str] = None
    ) -> int:
        """Actualiza un producto. Retorna filas afectadas."""
        ...
    # ↑ OPERACIÓN 4: ACTUALIZAR (UPDATE)
    # codigo: str → PK del producto a actualizar.
    # datos: dict[str, Any] → campos a modificar (sin incluir el código).
    #   Ejemplo: {"nombre": "Mouse Gamer", "stock": 15}
    # Retorna: int → número de filas afectadas (0 si no encontró el producto).

    async def eliminar(
        self,
        codigo: str,
        esquema: Optional[str] = None
    ) -> int:
        """Elimina un producto. Retorna filas eliminadas."""
        ...
    # ↑ OPERACIÓN 5: ELIMINAR (DELETE)
    # codigo: str → PK del producto a eliminar.
    # Retorna: int → número de filas eliminadas (0 si no existía).
```

**Resumen de las 5 operaciones del contrato:**

| # | Método | SQL equivalente | Parámetros | Retorna |
|---|--------|----------------|------------|---------|
| 1 | `obtener_todos()` | `SELECT * FROM producto LIMIT n` | esquema, limite | `list[dict]` |
| 2 | `obtener_por_codigo()` | `SELECT * FROM producto WHERE codigo = ?` | codigo, esquema | `list[dict]` |
| 3 | `crear()` | `INSERT INTO producto VALUES (...)` | datos, esquema | `bool` |
| 4 | `actualizar()` | `UPDATE producto SET ... WHERE codigo = ?` | codigo, datos, esquema | `int` |
| 5 | `eliminar()` | `DELETE FROM producto WHERE codigo = ?` | codigo, esquema | `int` |

---

## 3.4 `ProveedorConexion` — Implementación concreta

Este archivo **implementa** el contrato `IProveedorConexion`. Lee el `.env` a través de `config.py` y retorna la cadena de conexión del proveedor activo.

**Archivo:** `servicios/conexion/proveedor_conexion.py`

```python
"""Lee DB_PROVIDER y las cadenas de conexión desde .env."""
# ↑ Este módulo es la implementación concreta del contrato IProveedorConexion.
# Lee la configuración centralizada (config.py) y expone:
# 1. Qué proveedor de BD está activo (postgres, mysql, etc.)
# 2. La cadena de conexión correspondiente a ese proveedor.

from config import Settings, get_settings
# ↑ Importamos de nuestro config.py:
# Settings: la clase que contiene toda la configuración.
# get_settings: función singleton que retorna el objeto Settings cacheado.


class ProveedorConexion:
    """Lee el proveedor activo y entrega la cadena de conexión."""
    # ↑ Esta clase NO hereda de IProveedorConexion.
    # Sin embargo, CUMPLE el contrato porque tiene los mismos miembros:
    # - proveedor_actual (property → str)
    # - obtener_cadena_conexion() (método → str)
    # Esto es tipado estructural (duck typing) gracias a Protocol.

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
    # ↑ Constructor de la clase.
    # settings: Settings | None = None → parámetro opcional.
    #   Si le pasan un objeto Settings, lo usa directamente.
    #   Si no le pasan nada (None), llama a get_settings() para obtener el singleton.
    # self._settings → guarda la referencia como atributo privado (convención: _prefijo).
    # El "or" funciona así: si settings es None (falsy), usa get_settings().

    @property
    def proveedor_actual(self) -> str:
        """Proveedor activo según DB_PROVIDER en .env."""
        return self._settings.database.provider.lower().strip()
    # ↑ @property → se accede como atributo: proveedor.proveedor_actual (sin paréntesis).
    # self._settings.database → accede al objeto DatabaseSettings dentro de Settings.
    # .provider → campo que lee DB_PROVIDER del .env (ej: "postgres").
    # .lower() → convierte a minúsculas ("POSTGRES" → "postgres").
    # .strip() → elimina espacios en blanco al inicio/final (" postgres " → "postgres").

    def obtener_cadena_conexion(self) -> str:
        """Cadena de conexión del proveedor activo."""
        provider = self.proveedor_actual
        # ↑ Obtiene el nombre del proveedor normalizado (ej: "postgres").

        db_config = self._settings.database
        # ↑ Atajo: en vez de escribir self._settings.database cada vez,
        # guardamos la referencia en una variable local más corta.

        cadenas = {
            "postgres": db_config.postgres,
            "postgresql": db_config.postgres,
        }
        # ↑ Diccionario que mapea nombre de proveedor → cadena de conexión.
        # "postgres" y "postgresql" son aliases: ambos apuntan a la misma cadena.
        # db_config.postgres lee el campo 'postgres' de DatabaseSettings,
        # que a su vez leyó DB_POSTGRES del .env.
        #
        # NOTA: En el proyecto completo, este diccionario también incluye
        # sqlserver, mysql, mariadb, etc. Aquí solo usamos PostgreSQL.

        if provider not in cadenas:
            raise ValueError(
                f"Proveedor '{provider}' no soportado. "
                f"Opciones: {list(cadenas.keys())}"
            )
        # ↑ Validación: si el proveedor del .env no está en el diccionario,
        # lanza un error claro indicando qué opciones son válidas.
        # f"..." es un f-string: permite insertar variables dentro del texto.

        cadena = cadenas[provider]
        # ↑ Obtiene la cadena de conexión correspondiente al proveedor.

        if not cadena:
            raise ValueError(
                f"No se encontró cadena de conexión para '{provider}'. "
                f"Verificar DB_{provider.upper()} en .env"
            )
        # ↑ Validación: si la cadena está vacía (no se configuró en .env),
        # lanza un error indicando qué variable falta.
        # provider.upper() convierte "postgres" → "POSTGRES" para mostrar
        # el nombre correcto de la variable: DB_POSTGRES.

        return cadena
        # ↑ Retorna la cadena de conexión completa.
        # Ejemplo: "postgresql+asyncpg://postgres:postgres@localhost:5432/bdfacturas_postgres_local"
```

**Flujo completo cuando se llama a `obtener_cadena_conexion()`:**

```
1. ProveedorConexion.__init__()
   └── get_settings()                  ← Singleton: lee .env una sola vez
       └── Settings()
           └── DatabaseSettings()      ← Lee DB_PROVIDER y DB_POSTGRES del .env

2. obtener_cadena_conexion()
   ├── self.proveedor_actual           ← "postgres" (de DB_PROVIDER)
   ├── cadenas["postgres"]             ← "postgresql+asyncpg://postgres:..."
   ├── Validar que el proveedor existe ← OK
   ├── Validar que la cadena no está vacía ← OK
   └── return cadena                   ← "postgresql+asyncpg://postgres:postgres@localhost:5432/bdfacturas_postgres_local"
```

---

## 3.5 `BaseRepositorioPostgreSQL` — La clase base con toda la lógica SQL

Este es el **archivo más grande e importante** de la capa de datos (~350 líneas). Contiene toda la lógica SQL genérica para PostgreSQL: SELECT, INSERT, UPDATE, DELETE, detección de tipos y serialización.

**¿Por qué una clase "base"?** Porque esta clase **no sabe qué tabla maneja**. Solo tiene métodos protegidos (con prefijo `_`) que reciben el nombre de tabla como parámetro. La clase hija (`RepositorioProductoPostgreSQL`) le dice "la tabla es producto y la PK es codigo".

Esto es el **patrón Template Method**: la clase base define el algoritmo genérico, y la subclase llena los detalles específicos.

**Archivo:** `repositorios/base_repositorio_postgresql.py`

Lo dividimos en subsecciones para explicarlo mejor.

### 3.5.1 Imports y Constructor

```python
"""
base_repositorio_postgresql.py — Clase base con lógica SQL para PostgreSQL.

Características de PostgreSQL:
- Identificadores con "comillas dobles"
- LIMIT n para limitar resultados
- Esquema por defecto: 'public'
"""
# ↑ Docstring del módulo. Documenta las particularidades de PostgreSQL
# que se reflejan en el SQL generado por esta clase.
# - "comillas dobles": PostgreSQL usa "tabla" en vez de [tabla] (SQL Server)
#   o `tabla` (MySQL). Esto permite nombres con mayúsculas o espacios.
# - LIMIT n: PostgreSQL usa LIMIT (MySQL también), mientras que
#   SQL Server usa TOP n.
# - Esquema 'public': PostgreSQL organiza tablas en esquemas.
#   El esquema por defecto es 'public'.

from typing import Any
# ↑ Any: tipo comodín de Python. Acepta cualquier tipo.
# Lo usamos en dict[str, Any] porque las columnas de la BD pueden
# ser string, entero, decimal, fecha, booleano, etc.

from datetime import datetime, date, time
# ↑ Tipos de fecha/hora de Python.
# datetime: fecha + hora (2024-01-15 14:30:00)
# date: solo fecha (2024-01-15)
# time: solo hora (14:30:00)
# Los necesitamos para convertir valores que vienen de la BD.

from decimal import Decimal
# ↑ Tipo Decimal de Python: números con precisión exacta.
# Los campos NUMERIC(14,2) de PostgreSQL llegan como Decimal en Python.
# Ejemplo: Decimal('2500000.00') en vez de float 2500000.0
# Decimal es más preciso que float para valores monetarios.

from uuid import UUID
# ↑ Tipo UUID (Universally Unique Identifier).
# Es un identificador de 128 bits: "550e8400-e29b-41d4-a716-446655440000"
# Algunas tablas usan UUID como PK en vez de SERIAL o VARCHAR.

from sqlalchemy import text
# ↑ Función text() de SQLAlchemy.
# Permite escribir SQL crudo con parámetros seguros.
# text("SELECT * FROM producto WHERE codigo = :codigo")
# Los :parametros se reemplazan de forma segura (previene SQL injection).

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
# ↑ Componentes async de SQLAlchemy:
# create_async_engine: crea un pool de conexiones asíncronas.
#   Es la "puerta de entrada" a la base de datos.
# AsyncEngine: tipo del objeto engine (para type hints).

from servicios.abstracciones.i_proveedor_conexion import IProveedorConexion
# ↑ Importamos el contrato (interfaz) del proveedor de conexión.
# Esta clase base DEPENDE de la abstracción (IProveedorConexion),
# no de la implementación concreta (ProveedorConexion).
# Esto cumple el principio D de SOLID (Inversión de Dependencias).


class BaseRepositorioPostgreSQL:
    """Clase base con la lógica SQL de PostgreSQL. Los repositorios específicos heredan de esta clase."""
    # ↑ Esta clase es ABSTRACTA en el sentido de que no se usa directamente.
    # Siempre se usa a través de una subclase como RepositorioProductoPostgreSQL.
    # Los métodos empiezan con _ (protegidos): solo las subclases los llaman.

    def __init__(self, proveedor_conexion: IProveedorConexion):
        if proveedor_conexion is None:
            raise ValueError("proveedor_conexion no puede ser None")
        self._proveedor_conexion = proveedor_conexion
        self._engine: AsyncEngine | None = None
    # ↑ Constructor.
    # proveedor_conexion: IProveedorConexion → recibe el proveedor de conexión.
    #   El tipo es la INTERFAZ (Protocol), no la clase concreta.
    #   Esto es Inversión de Dependencias: depende de la abstracción.
    # Validación: si es None, lanza error inmediato (fail fast).
    # self._proveedor_conexion → guarda la referencia (atributo privado).
    # self._engine → el motor de conexión (se crea la primera vez que se necesita).
    #   Empieza como None y se inicializa en _obtener_engine() (lazy loading).

    async def _obtener_engine(self) -> AsyncEngine:
        """Crea el engine de conexión la primera vez, luego lo reutiliza."""
        if self._engine is None:
            cadena = self._proveedor_conexion.obtener_cadena_conexion()
            self._engine = create_async_engine(cadena, echo=False)
        return self._engine
    # ↑ Método asíncrono que retorna el engine de SQLAlchemy.
    # PATRÓN LAZY LOADING: no crea el engine hasta que realmente se necesita.
    # if self._engine is None → solo la primera vez:
    #   1. Obtiene la cadena de conexión del proveedor
    #   2. Crea el engine con create_async_engine()
    #      - cadena: "postgresql+asyncpg://postgres:...@localhost:5432/bdfacturas..."
    #      - echo=False: no imprime cada SQL en consola (True útil para debug)
    # Las siguientes llamadas retornan el engine ya creado (reutilización).
    #
    # ¿Qué es un engine?
    # Es un POOL de conexiones a la BD. No es una conexión individual.
    # SQLAlchemy mantiene varias conexiones abiertas y las reutiliza,
    # evitando el costo de abrir/cerrar conexiones constantemente.
```

### 3.5.2 Métodos auxiliares — Detección y conversión de tipos

Estos métodos ayudan a convertir valores entre Python y PostgreSQL. Son necesarios porque el JSON que envía el cliente HTTP siempre es texto, pero la BD espera tipos específicos (entero, decimal, fecha, etc.).

```python
    # ================================================================
    # MÉTODOS AUXILIARES — Detección y conversión de tipos
    # ================================================================

    async def _detectar_tipo_columna(
        self, nombre_tabla: str, esquema: str, nombre_columna: str
    ) -> str | None:
        """Consulta information_schema para saber el tipo de una columna."""
        sql = text("""
            SELECT data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema = :esquema
            AND table_name = :tabla
            AND column_name = :columna
        """)
        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql, {
                    "esquema": esquema, "tabla": nombre_tabla,
                    "columna": nombre_columna
                })
                row = result.fetchone()
                return row[0].lower() if row else None
        except Exception:
            return None
    # ↑ Consulta los METADATOS de PostgreSQL para saber el tipo de una columna.
    # information_schema.columns es una vista del sistema que describe todas las columnas
    # de todas las tablas. Es estándar SQL (existe en PostgreSQL, MySQL, SQL Server).
    #
    # Ejemplo: _detectar_tipo_columna("producto", "public", "stock")
    #   → Ejecuta: SELECT data_type FROM information_schema.columns
    #              WHERE table_schema='public' AND table_name='producto'
    #              AND column_name='stock'
    #   → Retorna: "integer"
    #
    # ¿Para qué sirve?
    # Cuando el cliente envía {"stock": "20"}, el valor llega como STRING.
    # Pero la columna stock es INTEGER. Necesitamos saber el tipo destino
    # para convertir "20" → 20 antes de hacer el INSERT/UPDATE.
    #
    # Los :parametros (:esquema, :tabla, :columna) son parámetros seguros.
    # SQLAlchemy los reemplaza de forma segura, previniendo SQL injection.
    #
    # async with engine.connect() as conn:
    #   → Obtiene una conexión del pool y la libera automáticamente al salir del bloque.
    # Si ocurre cualquier error, retorna None (la conversión se hará como string).

    def _convertir_valor(self, valor: str, tipo_destino: str | None) -> Any:
        """Convierte un string al tipo Python que corresponde."""
        if tipo_destino is None:
            return valor
        try:
            if tipo_destino in ('integer', 'int4', 'bigint', 'int8',
                                'smallint', 'int2'):
                return int(valor)
            if tipo_destino in ('numeric', 'decimal'):
                return Decimal(valor)
            if tipo_destino in ('real', 'float4', 'double precision', 'float8'):
                return float(valor)
            if tipo_destino in ('boolean', 'bool'):
                return valor.lower() in ('true', '1', 'yes', 'si', 't')
            if tipo_destino == 'uuid':
                return UUID(valor)
            if tipo_destino == 'date':
                return self._extraer_solo_fecha(valor)
            if tipo_destino in ('timestamp without time zone',
                                'timestamp with time zone'):
                return datetime.fromisoformat(valor.replace('Z', '+00:00'))
            if tipo_destino == 'time':
                return time.fromisoformat(valor)
            return valor
        except (ValueError, TypeError):
            return valor
    # ↑ Convierte un STRING al tipo Python que corresponde según el tipo de la columna.
    #
    # ¿Por qué es necesario?
    # Los datos JSON del cliente llegan como strings: {"stock": "20", "valorunitario": "50000.00"}
    # Pero PostgreSQL espera: stock=20 (int), valorunitario=50000.00 (Decimal).
    #
    # Tabla de conversiones:
    # | Tipo PostgreSQL              | Tipo Python | Ejemplo              |
    # |------------------------------|-------------|----------------------|
    # | integer, int4, bigint, int8  | int         | "20" → 20            |
    # | numeric, decimal             | Decimal     | "50000.00" → Decimal  |
    # | real, float4, double         | float       | "3.14" → 3.14        |
    # | boolean, bool                | bool        | "true" → True         |
    # | uuid                         | UUID        | "550e8400-..." → UUID |
    # | date                         | date        | "2024-01-15" → date   |
    # | timestamp                    | datetime    | "2024-01-15T14:30" → datetime |
    # | time                         | time        | "14:30:00" → time     |
    #
    # Si el tipo es None (no se pudo detectar) o la conversión falla,
    # retorna el valor original como string (mejor que lanzar error).
    #
    # Para la tabla producto:
    # - codigo (VARCHAR) → se queda como str
    # - nombre (VARCHAR) → se queda como str
    # - stock (INTEGER) → "20" se convierte a int(20)
    # - valorunitario (NUMERIC) → "50000.00" se convierte a Decimal("50000.00")

    def _extraer_solo_fecha(self, valor: str) -> date:
        """Extrae la parte de fecha de un string ISO."""
        if 'T' in valor:
            return datetime.fromisoformat(
                valor.replace('Z', '+00:00')
            ).date()
        return date.fromisoformat(valor[:10])
    # ↑ Convierte un string de fecha a un objeto date de Python.
    # Si el string incluye hora ("2024-01-15T14:30:00"), extrae solo la fecha.
    # Si es solo fecha ("2024-01-15"), lo convierte directamente.
    # .replace('Z', '+00:00') → convierte formato UTC de JavaScript a ISO Python.
    # valor[:10] → toma solo los primeros 10 caracteres: "2024-01-15".

    def _es_fecha_sin_hora(self, valor: str) -> bool:
        """Detecta si un valor tiene formato YYYY-MM-DD (solo fecha)."""
        return (len(valor) == 10 and valor.count('-') == 2
                and 'T' not in valor)
    # ↑ Verifica si un string es una fecha pura (sin hora).
    # Condiciones: exactamente 10 caracteres, 2 guiones, sin 'T'.
    # "2024-01-15" → True (fecha pura)
    # "2024-01-15T14:30:00" → False (tiene hora)
    # Se usa en _obtener_por_clave para decidir si comparar
    # una columna TIMESTAMP solo por la parte DATE.

    def _serializar_valor(self, valor: Any) -> Any:
        """Convierte tipos Python a tipos serializables para JSON."""
        if isinstance(valor, (datetime, date)):
            return valor.isoformat()
        elif isinstance(valor, Decimal):
            return float(valor)
        elif isinstance(valor, UUID):
            return str(valor)
        return valor
    # ↑ Convierte tipos Python a tipos que JSON puede representar.
    # FastAPI necesita devolver JSON al cliente, pero JSON no tiene
    # tipos nativos para fecha, Decimal o UUID.
    #
    # Conversiones:
    # | Tipo Python | Tipo JSON | Ejemplo                          |
    # |-------------|-----------|----------------------------------|
    # | datetime    | string    | datetime(2024,1,15) → "2024-01-15T00:00:00" |
    # | date        | string    | date(2024,1,15) → "2024-01-15"   |
    # | Decimal     | number    | Decimal('2500000.00') → 2500000.0|
    # | UUID        | string    | UUID('550e...') → "550e8400-..."  |
    # | otros       | sin cambio| "Laptop" → "Laptop", 20 → 20     |
    #
    # isinstance(valor, (datetime, date)) → True si valor es datetime O date.
    # .isoformat() → convierte a string formato ISO 8601.
```

### 3.5.3 Operación 1: LISTAR — `_obtener_filas()`

```python
    # ================================================================
    # OPERACIÓN 1: LISTAR (SELECT * LIMIT n)
    # ================================================================

    async def _obtener_filas(
        self, nombre_tabla: str, esquema: str | None = None,
        limite: int | None = None
    ) -> list[dict[str, Any]]:
        """Obtiene filas de una tabla con LIMIT opcional."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        # ↑ Validación: si el nombre de tabla es vacío o solo espacios, error.
        # "not nombre_tabla" captura None y "".
        # "not nombre_tabla.strip()" captura "   " (solo espacios).

        esquema_final = (esquema or "public").strip()
        # ↑ Si esquema es None o vacío, usa "public" (esquema por defecto de PostgreSQL).
        # .strip() elimina espacios en blanco.
        # "or" funciona: si esquema es None/""/"  " (falsy), usa "public".

        limite_final = limite or 1000
        # ↑ Si limite es None o 0, usa 1000 como máximo por defecto.
        # Esto evita traer millones de filas sin querer.

        sql = text(
            f'SELECT * FROM "{esquema_final}"."{nombre_tabla}" LIMIT :limite'
        )
        # ↑ Construye el SQL con f-string para tabla/esquema y :parámetro para LIMIT.
        # Resultado: SELECT * FROM "public"."producto" LIMIT :limite
        #
        # ¿Por qué "comillas dobles"?
        # PostgreSQL usa "comillas dobles" para identificadores (nombres de tablas/columnas).
        # Esto permite nombres con mayúsculas, espacios o palabras reservadas.
        #
        # ¿Por qué :limite y no f-string para el valor?
        # SEGURIDAD: :limite es un parámetro que SQLAlchemy reemplaza de forma segura.
        # Si usáramos f-string para valores, sería vulnerable a SQL injection.
        # Regla: nombres de tabla/esquema en f-string, VALORES siempre con :parametro.

        try:
            engine = await self._obtener_engine()
            # ↑ Obtiene el engine (pool de conexiones). Lazy loading.

            async with engine.connect() as conn:
                # ↑ Obtiene una conexión del pool.
                # "async with" garantiza que la conexión se libere al salir del bloque,
                # incluso si ocurre un error. Es como un try/finally automático.

                result = await conn.execute(sql, {"limite": limite_final})
                # ↑ Ejecuta el SQL con los parámetros.
                # await → espera la respuesta de la BD sin bloquear el hilo.
                # {"limite": limite_final} → reemplaza :limite por el valor (ej: 1000).

                columnas = result.keys()
                # ↑ Obtiene los nombres de las columnas del resultado.
                # Ejemplo: ["codigo", "nombre", "stock", "valorunitario"]

                return [
                    {col: self._serializar_valor(row[i])
                     for i, col in enumerate(columnas)}
                    for row in result.fetchall()
                ]
                # ↑ List comprehension + dict comprehension.
                # result.fetchall() → obtiene TODAS las filas como tuplas.
                # Para cada fila (row), crea un diccionario:
                #   enumerate(columnas) → [(0, "codigo"), (1, "nombre"), (2, "stock"), ...]
                #   row[i] → valor en la posición i de la tupla
                #   self._serializar_valor(row[i]) → convierte Decimal, date, etc. a JSON
                #
                # Ejemplo de transformación:
                #   Fila tupla: ("PR001", "Laptop Lenovo", 20, Decimal('2500000.00'))
                #   → Diccionario: {"codigo": "PR001", "nombre": "Laptop Lenovo",
                #                    "stock": 20, "valorunitario": 2500000.0}

        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al consultar "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex
        # ↑ Si ocurre cualquier error (conexión, SQL, etc.):
        # - Captura la excepción original (ex)
        # - Lanza una RuntimeError con un mensaje descriptivo
        # - "from ex" conserva la excepción original en la cadena de errores
        #   (útil para depuración: puedes ver el error original en el traceback)
```

### 3.5.4 Operación 2: BUSCAR POR CLAVE — `_obtener_por_clave()`

```python
    # ================================================================
    # OPERACIÓN 2: BUSCAR POR CLAVE (SELECT * WHERE clave = valor)
    # ================================================================

    async def _obtener_por_clave(
        self, nombre_tabla: str, nombre_clave: str, valor: str,
        esquema: str | None = None
    ) -> list[dict[str, Any]]:
        """Obtiene filas filtradas por una columna y valor."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío")
        if not valor or not valor.strip():
            raise ValueError("El valor no puede estar vacío")
        # ↑ Validaciones de entrada: ningún parámetro puede estar vacío.
        # nombre_clave es el nombre de la columna PK (ej: "codigo").
        # valor es el valor a buscar (ej: "PR001").

        esquema_final = (esquema or "public").strip()
        # ↑ Esquema por defecto: "public".

        try:
            tipo_columna = await self._detectar_tipo_columna(
                nombre_tabla, esquema_final, nombre_clave
            )
            # ↑ Consulta information_schema para saber el tipo de la columna PK.
            # Para producto.codigo → retorna "character varying" (VARCHAR).

            # Si buscan una fecha en una columna TIMESTAMP,
            # comparar solo la parte DATE
            if (tipo_columna in ('timestamp without time zone',
                                 'timestamp with time zone')
                    and self._es_fecha_sin_hora(valor)):
                sql = text(f'''
                    SELECT * FROM "{esquema_final}"."{nombre_tabla}"
                    WHERE CAST("{nombre_clave}" AS DATE) = :valor
                ''')
                valor_convertido = self._extraer_solo_fecha(valor)
            # ↑ Caso especial: si la columna es TIMESTAMP pero el usuario busca
            # por fecha sin hora ("2024-01-15"), hace CAST a DATE para comparar
            # solo la parte de fecha. Esto no aplica a producto (no tiene timestamps).
            else:
                sql = text(f'''
                    SELECT * FROM "{esquema_final}"."{nombre_tabla}"
                    WHERE "{nombre_clave}" = :valor
                ''')
                valor_convertido = self._convertir_valor(
                    valor, tipo_columna
                )
            # ↑ Caso normal: SELECT * WHERE "codigo" = :valor
            # Convierte el valor al tipo correcto antes de ejecutar.
            # Para producto: "PR001" → "PR001" (VARCHAR no necesita conversión).

            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(
                    sql, {"valor": valor_convertido}
                )
                columnas = result.keys()
                return [
                    {col: self._serializar_valor(row[i])
                     for i, col in enumerate(columnas)}
                    for row in result.fetchall()
                ]
            # ↑ Ejecuta el SQL, serializa y retorna la lista de diccionarios.
            # Si PR001 existe: [{"codigo": "PR001", "nombre": "Laptop", ...}]
            # Si no existe: [] (lista vacía)

        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al filtrar "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex
```

### 3.5.5 Operación 3: CREAR — `_crear()`

```python
    # ================================================================
    # OPERACIÓN 3: CREAR (INSERT INTO tabla VALUES (...))
    # ================================================================

    async def _crear(
        self, nombre_tabla: str, datos: dict[str, Any],
        esquema: str | None = None
    ) -> bool:
        """Inserta una nueva fila en la tabla."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos")
        # ↑ Validaciones: tabla y datos son obligatorios.
        # datos es un dict como: {"codigo": "PR006", "nombre": "Mouse", "stock": 10, ...}

        esquema_final = (esquema or "public").strip()
        datos_finales = dict(datos)
        # ↑ dict(datos) crea una COPIA del diccionario original.
        # Trabajamos sobre la copia para no modificar el diccionario que nos pasaron.

        columnas = ", ".join(f'"{k}"' for k in datos_finales.keys())
        # ↑ Construye la lista de columnas para el INSERT.
        # datos_finales.keys() → ["codigo", "nombre", "stock", "valorunitario"]
        # f'"{k}"' → envuelve cada nombre en "comillas dobles" (sintaxis PostgreSQL)
        # ", ".join(...) → une con comas: "codigo", "nombre", "stock", "valorunitario"

        parametros = ", ".join(f":{k}" for k in datos_finales.keys())
        # ↑ Construye los placeholders para los valores.
        # :codigo, :nombre, :stock, :valorunitario
        # SQLAlchemy reemplazará cada :placeholder por su valor de forma segura.

        sql = text(
            f'INSERT INTO "{esquema_final}"."{nombre_tabla}" '
            f'({columnas}) VALUES ({parametros})'
        )
        # ↑ SQL final:
        # INSERT INTO "public"."producto"
        # ("codigo", "nombre", "stock", "valorunitario")
        # VALUES (:codigo, :nombre, :stock, :valorunitario)
        #
        # Los valores NO están en el SQL — están como :parámetros seguros.
        # Esto previene SQL injection.

        try:
            valores = {}
            for key, val in datos_finales.items():
                if val is not None and isinstance(val, str):
                    tipo = await self._detectar_tipo_columna(
                        nombre_tabla, esquema_final, key
                    )
                    valores[key] = self._convertir_valor(val, tipo)
                else:
                    valores[key] = val
            # ↑ Para cada campo, detecta el tipo de la columna y convierte el valor.
            # Solo convierte si el valor es un STRING (los que ya son int/float se mantienen).
            # Ejemplo:
            #   "codigo": "PR006" → tipo=VARCHAR → se queda "PR006"
            #   "stock": "10" → tipo=INTEGER → se convierte a int(10)
            #   "stock": 10 → ya es int, no se convierte (no pasa por el if)

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(sql, valores)
                return result.rowcount > 0
            # ↑ IMPORTANTE: engine.begin() en vez de engine.connect()
            # engine.begin() abre una TRANSACCIÓN:
            #   - Si todo sale bien, hace COMMIT automáticamente al salir del bloque
            #   - Si ocurre un error, hace ROLLBACK automáticamente
            # Esto garantiza que el INSERT sea atómico (todo o nada).
            #
            # result.rowcount → número de filas afectadas por el INSERT.
            # Si es > 0, el INSERT fue exitoso → retorna True.
            # Si es 0, no se insertó nada → retorna False.

        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al insertar en "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex
```

### 3.5.6 Operación 4: ACTUALIZAR — `_actualizar()`

```python
    # ================================================================
    # OPERACIÓN 4: ACTUALIZAR (UPDATE tabla SET ... WHERE ...)
    # ================================================================

    async def _actualizar(
        self, nombre_tabla: str, nombre_clave: str, valor_clave: str,
        datos: dict[str, Any], esquema: str | None = None
    ) -> int:
        """Actualiza filas. Retorna filas afectadas."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío")
        if not valor_clave or not valor_clave.strip():
            raise ValueError("El valor de la clave no puede estar vacío")
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos")
        # ↑ Validaciones: todos los parámetros son obligatorios para un UPDATE.
        # nombre_clave: nombre de la columna PK (ej: "codigo")
        # valor_clave: valor de la PK del registro a actualizar (ej: "PR001")
        # datos: campos a modificar (ej: {"nombre": "Laptop Gamer", "stock": 15})

        esquema_final = (esquema or "public").strip()
        datos_finales = dict(datos)
        # ↑ Copia del diccionario para no modificar el original.

        clausula_set = ", ".join(
            f'"{k}" = :{k}' for k in datos_finales.keys()
        )
        # ↑ Construye la cláusula SET del UPDATE.
        # datos_finales.keys() → ["nombre", "stock"]
        # f'"{k}" = :{k}' → "nombre" = :nombre, "stock" = :stock
        # Resultado: "nombre" = :nombre, "stock" = :stock

        sql = text(f'''
            UPDATE "{esquema_final}"."{nombre_tabla}"
            SET {clausula_set}
            WHERE "{nombre_clave}" = :valor_clave
        ''')
        # ↑ SQL final:
        # UPDATE "public"."producto"
        # SET "nombre" = :nombre, "stock" = :stock
        # WHERE "codigo" = :valor_clave
        #
        # Nota: la PK usa el nombre fijo :valor_clave para no confundirse
        # con los campos del SET (que usan el nombre de la columna).

        try:
            valores = {}
            for key, val in datos_finales.items():
                if val is not None and isinstance(val, str):
                    tipo = await self._detectar_tipo_columna(
                        nombre_tabla, esquema_final, key
                    )
                    valores[key] = self._convertir_valor(val, tipo)
                else:
                    valores[key] = val
            # ↑ Conversión de tipos para los campos del SET (igual que en _crear).

            tipo_clave = await self._detectar_tipo_columna(
                nombre_tabla, esquema_final, nombre_clave
            )
            valores["valor_clave"] = self._convertir_valor(
                valor_clave, tipo_clave
            )
            # ↑ También convierte el valor de la PK al tipo correcto.
            # Para producto.codigo (VARCHAR): "PR001" → "PR001" (sin cambio).
            # Para una tabla con PK INTEGER: "42" → 42.

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(sql, valores)
                return result.rowcount
            # ↑ Transacción automática (begin = commit o rollback).
            # result.rowcount → filas afectadas.
            # Si PR001 existe y se actualizó: retorna 1.
            # Si PR001 no existe: retorna 0.

        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al actualizar "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex
```

### 3.5.7 Operación 5: ELIMINAR — `_eliminar()`

```python
    # ================================================================
    # OPERACIÓN 5: ELIMINAR (DELETE FROM tabla WHERE ...)
    # ================================================================

    async def _eliminar(
        self, nombre_tabla: str, nombre_clave: str, valor_clave: str,
        esquema: str | None = None
    ) -> int:
        """Elimina filas. Retorna filas eliminadas."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío")
        if not valor_clave or not valor_clave.strip():
            raise ValueError("El valor de la clave no puede estar vacío")
        # ↑ Validaciones: tabla, clave y valor son obligatorios.

        esquema_final = (esquema or "public").strip()

        sql = text(f'''
            DELETE FROM "{esquema_final}"."{nombre_tabla}"
            WHERE "{nombre_clave}" = :valor_clave
        ''')
        # ↑ SQL: DELETE FROM "public"."producto" WHERE "codigo" = :valor_clave
        # Solo elimina las filas que coincidan con la PK.

        try:
            tipo_clave = await self._detectar_tipo_columna(
                nombre_tabla, esquema_final, nombre_clave
            )
            valor_convertido = self._convertir_valor(
                valor_clave, tipo_clave
            )
            # ↑ Convierte el valor de la PK al tipo correcto.

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(
                    sql, {"valor_clave": valor_convertido}
                )
                return result.rowcount
            # ↑ Transacción automática.
            # result.rowcount → filas eliminadas.
            # Si PR001 existía: retorna 1.
            # Si PR001 no existía: retorna 0.

        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al eliminar de "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex
```

---

## 3.6 `RepositorioProductoPostgreSQL` — El repositorio específico

Este es el archivo **más corto** de la capa de datos (~37 líneas). Solo le dice a la clase base: "la tabla es `producto` y la clave primaria es `codigo`". Toda la lógica SQL ya está resuelta en `BaseRepositorioPostgreSQL`.

Esto es el **patrón Template Method** en acción: la clase base tiene el algoritmo genérico, la subclase solo rellena los datos específicos.

**Archivo:** `repositorios/producto/repositorio_producto_postgresql.py`

```python
"""Repositorio de producto para PostgreSQL."""
# ↑ Docstring del módulo: este archivo contiene la implementación
# concreta del repositorio de producto para PostgreSQL.

from repositorios.base_repositorio_postgresql import BaseRepositorioPostgreSQL
# ↑ Importamos la clase base que tiene toda la lógica SQL.
# Esta clase hereda de ella para reutilizar los 5 métodos protegidos:
# _obtener_filas, _obtener_por_clave, _crear, _actualizar, _eliminar.


class RepositorioProductoPostgreSQL(BaseRepositorioPostgreSQL):
    """Acceso a datos de producto en PostgreSQL."""
    # ↑ Hereda de BaseRepositorioPostgreSQL.
    # Esto le da acceso a TODOS los métodos de la clase base.
    # Esta clase no necesita el constructor (__init__) porque
    # usa el del padre (que recibe proveedor_conexion).

    TABLA = "producto"
    # ↑ Constante de clase: nombre de la tabla en la BD.
    # Se pasa como parámetro a los métodos de la clase base.

    CLAVE_PRIMARIA = "codigo"
    # ↑ Constante de clase: nombre de la columna PK.
    # Se pasa como parámetro a _obtener_por_clave, _actualizar, _eliminar.

    async def obtener_todos(self, esquema=None, limite=None):
        """Obtiene todos los productos."""
        return await self._obtener_filas(self.TABLA, esquema, limite)
    # ↑ OPERACIÓN 1: LISTAR
    # Delega completamente a la clase base.
    # self.TABLA → "producto"
    # Resultado: SELECT * FROM "public"."producto" LIMIT 1000

    async def obtener_por_codigo(self, codigo, esquema=None):
        """Obtiene un producto por su codigo."""
        return await self._obtener_por_clave(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )
    # ↑ OPERACIÓN 2: BUSCAR POR CÓDIGO
    # self.TABLA → "producto", self.CLAVE_PRIMARIA → "codigo"
    # str(codigo) → convierte a string por seguridad.
    # Resultado: SELECT * FROM "public"."producto" WHERE "codigo" = :valor

    async def crear(self, datos, esquema=None):
        """Crea un nuevo producto."""
        return await self._crear(self.TABLA, datos, esquema)
    # ↑ OPERACIÓN 3: CREAR
    # datos es un dict: {"codigo": "PR006", "nombre": "Mouse", "stock": 10, ...}
    # Resultado: INSERT INTO "public"."producto" ("codigo", ...) VALUES (:codigo, ...)

    async def actualizar(self, codigo, datos, esquema=None):
        """Actualiza un producto existente."""
        return await self._actualizar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), datos, esquema
        )
    # ↑ OPERACIÓN 4: ACTUALIZAR
    # Resultado: UPDATE "public"."producto" SET ... WHERE "codigo" = :valor_clave

    async def eliminar(self, codigo, esquema=None):
        """Elimina un producto por su codigo."""
        return await self._eliminar(
            self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema
        )
    # ↑ OPERACIÓN 5: ELIMINAR
    # Resultado: DELETE FROM "public"."producto" WHERE "codigo" = :valor_clave
```

**Así funciona Template Method en este proyecto:**

```
BaseRepositorioPostgreSQL (clase base genérica)
├── _obtener_filas(tabla, esquema, limite)     ← SQL genérico
├── _obtener_por_clave(tabla, clave, valor)    ← SQL genérico
├── _crear(tabla, datos)                       ← SQL genérico
├── _actualizar(tabla, clave, valor, datos)    ← SQL genérico
└── _eliminar(tabla, clave, valor)             ← SQL genérico

RepositorioProductoPostgreSQL (subclase específica)
├── TABLA = "producto"                         ← dato específico
├── CLAVE_PRIMARIA = "codigo"                  ← dato específico
├── obtener_todos() → _obtener_filas("producto", ...)
├── obtener_por_codigo() → _obtener_por_clave("producto", "codigo", ...)
├── crear() → _crear("producto", ...)
├── actualizar() → _actualizar("producto", "codigo", ...)
└── eliminar() → _eliminar("producto", "codigo", ...)
```

**¿Cómo agregarías otro repositorio (ej: `factura`)?**

Solo creas una nueva clase con TABLA = "factura" y CLAVE_PRIMARIA = "numero". ¡Cero cambios en la clase base! Esto es el principio **Open/Closed** de SOLID.

---

## 3.7 Archivos `__init__.py` — Exports de los paquetes

Los archivos `__init__.py` permiten importar las clases con rutas cortas. En vez de escribir la ruta completa del archivo, puedes importar directamente desde el paquete.

### `repositorios/__init__.py`

```python
"""Paquete de repositorios — Clase base de PostgreSQL."""

from .base_repositorio_postgresql import BaseRepositorioPostgreSQL
# ↑ El punto (.) significa "desde este mismo paquete".
# Hace que BaseRepositorioPostgreSQL sea importable como:
#   from repositorios import BaseRepositorioPostgreSQL
# En vez de:
#   from repositorios.base_repositorio_postgresql import BaseRepositorioPostgreSQL
```

### `repositorios/producto/__init__.py`

```python
"""Repositorios específicos de producto."""

from .repositorio_producto_postgresql import RepositorioProductoPostgreSQL
# ↑ Exporta la clase para poder importarla como:
#   from repositorios.producto import RepositorioProductoPostgreSQL
```

---

## Resumen de la Parte 3

### Archivos creados

| # | Archivo | Capa | Líneas | Propósito |
|---|---------|------|--------|-----------|
| 1 | `servicios/abstracciones/i_proveedor_conexion.py` | Abstracción | 17 | Contrato: qué proveedor está activo y su cadena de conexión |
| 2 | `repositorios/abstracciones/i_repositorio_producto.py` | Abstracción | 48 | Contrato: 5 operaciones CRUD para producto |
| 3 | `servicios/conexion/proveedor_conexion.py` | Datos | 46 | Lee DB_PROVIDER y DB_POSTGRES del .env |
| 4 | `repositorios/base_repositorio_postgresql.py` | Datos | ~350 | Lógica SQL genérica: SELECT, INSERT, UPDATE, DELETE + conversión de tipos |
| 5 | `repositorios/producto/repositorio_producto_postgresql.py` | Datos | 37 | TABLA="producto", CLAVE_PRIMARIA="codigo", 5 métodos delegando a la base |
| 6 | `repositorios/__init__.py` | Config | 3 | Export de BaseRepositorioPostgreSQL |
| 7 | `repositorios/producto/__init__.py` | Config | 3 | Export de RepositorioProductoPostgreSQL |

### Patrones aplicados en esta parte

| Patrón | Dónde | Qué resuelve |
|--------|-------|-------------|
| **Protocol (Interface)** | `IProveedorConexion`, `IRepositorioProducto` | Contratos sin herencia obligatoria |
| **Template Method** | `BaseRepositorioPostgreSQL` → `RepositorioProductoPostgreSQL` | Lógica SQL genérica, datos específicos en subclase |
| **Lazy Loading** | `_obtener_engine()` | El engine se crea solo cuando se necesita |
| **Inversión de Dependencias** | `BaseRepositorioPostgreSQL` recibe `IProveedorConexion` | Depende de abstracción, no de implementación concreta |

### Diagrama de dependencias

```
IProveedorConexion (Protocol)        IRepositorioProducto (Protocol)
        ↑ cumple                              ↑ cumple
        │                                     │
ProveedorConexion ──────────→ BaseRepositorioPostgreSQL
  (lee .env vía config.py)           ↑ hereda
                                     │
                         RepositorioProductoPostgreSQL
                         (TABLA="producto", CLAVE="codigo")
```

---

## Siguiente paso

En la **Parte 4** construiremos la **capa de negocio**: la interfaz `IServicioProducto`, el servicio `ServicioProducto` (validaciones y lógica) y la fábrica `fabrica_repositorios.py` (que conecta todo usando el patrón Factory). Es la capa que orquesta la comunicación entre el controller y el repositorio.

---

> **Nota:** Al terminar esta parte, aún no puedes ejecutar la API. Pero ya tienes toda la capa de datos funcional: interfaces, conexión, SQL genérico y el repositorio de producto. En la Parte 5 crearemos los endpoints HTTP y en la Parte 6 el `main.py` para ejecutar.
