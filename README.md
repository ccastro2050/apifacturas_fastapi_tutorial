# API Facturas FastAPI - Tutorial

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
</p>

> **Proyecto Tutorial**: API RESTful desarrollada con FastAPI implements una arquitectura de 3 capas (Presentacion, Negocio, Datos) para gestionar productos en una base de datos PostgreSQL.

## Tabla de Contenidos

1. [Descripcion del Proyecto](#descripcion-del-proyecto)
2. [Arquitectura](#arquitectura)
3. [Tecnologias](#tecnologias)
4. [Prerrequisitos](#prerrequisitos)
5. [Instalacion](#instalacion)
6. [Configuracion](#configuracion)
7. [Ejecucion](#ejecucion)
8. [Endpoints de la API](#endpoints-de-la-api)
9. [Estructura del Proyecto](#estructura-del-proyecto)
10. [Conceptos Clave](#conceptos-clave)
11. [Tutorial Completo](#tutorial-completo)
12. [Licencia](#licencia)

---

## Descripcion del Proyecto

Este proyecto es un **tutorial completo** de FastAPI que demuestra como construir una API REST con arquitectura de 3 capas. Aunque el nombre sugiere un sistema de facturas, el tutorial se enfoca en la entidad **Producto** como ejemplo didactico para ensenar los patrones de diseno esenciales.

### Caracteristicas Principales

- **CRUD Completo**: Create, Read, Update, Delete para la entidad Producto
- **Arquitectura de 3 Capas**: Separacion clara entre presentacion, negocio y datos
- **Base de Datos Asincrona**: PostgreSQL con driver asyncpg
- **Validacion Automatica**: Pydantic valida los datos de entrada
- **Documentacion Interactiva**: Swagger UI y ReDoc integrados
- **Configuracion por Entornos**: Desarrollo y Produccion con .env

---

## Arquitectura

El proyecto implementa una **Arquitectura de 3 Capas** (Layered Architecture) siguiendo principios SOLID:

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACION                     │
│  (Controllers - FastAPI Routers)                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  producto_controller.py                             │   │
│  │  - Valida rutas HTTP                                 │   │
│  │  - Maneja respuestas JSON                            │   │
│  │  - Delega a la capa de servicio                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      CAPA DE NEGOCIO                         │
│  (Servicios - Business Logic)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  servicio_producto.py                               │   │
│  │  - Valida reglas de negocio                          │   │
│  │  - Normaliza parametros                              │   │
│  │  - Delega al repositorio                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       CAPA DE DATOS                          │
│  (Repositorios - Data Access)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  RepositorioProductoPostgreSQL                       │   │
│  │  - Ejecuta queries SQL                               │   │
│  │  - Maneja conexiones a la BD                         │   │
│  │  - Detecta tipos de columnas                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de una Peticion

```
Cliente HTTP
     │
     ▼
┌─────────────────┐
│  FastAPI Router │  ← Capa de Presentacion
│ (Controller)    │    Valida endpoints y serializa respuestas
└────────┬────────┘
         │ crear_servicio_producto()
         ▼
┌─────────────────┐
│  Servicio       │  ← Capa de Negocio
│ (Business Logic)│    Valida reglas de negocio
└────────┬────────┘
         │ repo.obtener_todos()
         ▼
┌─────────────────┐
│  Repositorio    │  ← Capa de Datos
│ (Data Access)   │    Ejecuta SQL en PostgreSQL
└─────────────────┘
```

---

## Tecnologias

| Categoria | Tecnologia | Version | Descripcion |
|-----------|------------|---------|-------------|
| **Framework** | FastAPI | >=0.100.0 | Framework web asincrono |
| **Servidor** | Uvicorn | >=0.22.0 | Servidor ASGI |
| **Validacion** | Pydantic | >=2.0.0 | Validacion de datos |
| **Configuracion** | pydantic-settings | >=2.0.0 | Lectura de archivos .env |
| **Base de Datos** | PostgreSQL | - | Motor de base de datos |
| **Driver BD** | asyncpg | >=0.28.0 | Driver asincrono para PostgreSQL |
| **ORM/Query Builder** | SQLAlchemy | >=2.0.0 | Construccion de queries |

---

## Prerrequisitos

Antes de ejecutar el proyecto, asegurate de tener instalado:

1. **Python 3.10+**
   ```bash
   python --version
   ```

2. **PostgreSQL 14+** (o usar Docker)
   ```bash
   psql --version
   ```

3. **Git** (opcional, para clonar el repositorio)

---

## Instalacion

### 1. Clonar o descargar el proyecto

```bash
cd c:/Users/fcl/OneDrive/Desktop/proyectospython/apifacturas_fastapi_tutorial
```

### 2. Crear un entorno virtual (recomendado)

```bash
# En Windows
python -m venv venv

# Activar el entorno virtual
venv\Scripts\activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

---

## Configuracion

### Archivo `.env`

Crea un archivo `.env` en la raiz del proyecto con la siguiente configuracion:

```env
# ============================================
# CONFIGURACION DE ENTORNO
# ============================================

# Entorno de ejecucion: "development" o "production"
ENVIRONMENT=development

# Modo debug (True/False)
DEBUG=True

# ============================================
# CONFIGURACION DE BASE DE DATOS
# ============================================

# Proveedor de base de datos (postgres, mysql, etc.)
DB_PROVIDER=postgres

# Cadena de conexion PostgreSQL
# Formato: postgresql+asyncpg://usuario:password@host:puerto/nombre_base
DB_POSTGRES=postgresql+asyncpg://postgres:postgres@localhost:5432/facturas
```

### Archivo `.env.development` (opcional)

Para desarrollo, puedes crear un archivo `.env.development` que sobrescribira los valores de `.env`:

```env
ENVIRONMENT=development
DEBUG=True
DB_POSTGRES=postgresql+asyncpg://postgres:postgres@localhost:5432/facturas
```

### Configuracion de PostgreSQL

1. **Crear la base de datos**:
   ```sql
   CREATE DATABASE facturas;
   ```

2. **Ejecutar el script SQL**:
   El archivo `database/bdfacturas_postgres.sql` contiene el esquema completo de la base de datos.
   ```bash
   psql -U postgres -d facturas -f database/bdfacturas_postgres.sql
   ```

---

## Ejecucion

### Iniciar el servidor de desarrollo

```bash
uvicorn main:app --reload
```

El servidor iniciara en: `http://localhost:8000`

### Documentacion Interactiva

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Verificar que la API esta activa

Visita: `http://localhost:8000/`

Deberias ver:
```json
{
  "mensaje": "API Producto - Tutorial FastAPI activa.",
  "documentacion": "/docs",
  "documentacion_alternativa": "/redoc"
}
```

---

## Endpoints de la API

La API proporciona los siguientes endpoints para la entidad **Producto**:

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| `GET` | `/api/producto/` | Listar todos los productos |
| `GET` | `/api/producto/{codigo}` | Obtener un producto por codigo |
| `POST` | `/api/producto/` | Crear un nuevo producto |
| `PUT` | `/api/producto/{codigo}` | Actualizar un producto |
| `DELETE` | `/api/producto/{codigo}` | Eliminar un producto |

### Parametros de Query

Todos los endpoints aceptan parametros opcionales:

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `esquema` | string | Esquema de la base de datos (default: "public") |
| `limite` | integer | Numero maximo de resultados (default: 1000) |

### Ejemplos de Uso

#### 1. Listar productos
```bash
GET http://localhost:8000/api/producto/
```

#### 2. Obtener producto por codigo
```bash
GET http://localhost:8000/api/producto/PR001
```

#### 3. Crear producto
```bash
POST http://localhost:8000/api/producto/
Content-Type: application/json

{
  "codigo": "PR006",
  "nombre": "Mouse Gamer",
  "stock": 50,
  "valorunitario": 150000.00
}
```

#### 4. Actualizar producto
```bash
PUT http://localhost:8000/api/producto/PR001
Content-Type: application/json

{
  "nombre": "Laptop Gamer Pro",
  "stock": 15,
  "valorunitario": 3500000.00
}
```

#### 5. Eliminar producto
```bash
DELETE http://localhost:8000/api/producto/PR001
```

---

## Estructura del Proyecto

```
apifacturas_fastapi_tutorial/
├── main.py                           # Punto de entrada de la aplicacion
├── config.py                         # Configuracion centralizada
├── requirements.txt                  # Dependencias Python
├── .gitignore                        # Archivos ignorados por Git
│
├── models/                           # Modelos Pydantic (validacion de datos)
│   ├── __init__.py
│   └── producto.py                   # Modelo de Producto
│
├── controllers/                      # Capa de presentacion (Routers FastAPI)
│   ├── __init__.py
│   └── producto_controller.py        # Endpoints HTTP de Producto
│
├── servicios/                        # Capa de negocio (Business Logic)
│   ├── __init__.py
│   ├── servicio_producto.py          # Logica de negocio de Producto
│   ├── fabrica_repositorios.py      # Factory para crear servicios
│   │
│   ├── abstracciones/                # Contratos/Interfaces
│   │   ├── i_servicio_producto.py   # Interfaz de servicio
│   │   └── i_proveedor_conexion.py  # Interfaz de conexion
│   │
│   └── conexion/                     # Gestion de conexiones
│       └── proveedor_conexion.py     # Proveedor de conexion a BD
│
├── repositorios/                     # Capa de datos (Data Access)
│   ├── __init__.py
│   ├── base_repositorio_postgresql.py  # Clase base con SQL generico
│   │
│   ├── abstracciones/                # Contratos/Interfaces
│   │   └── i_repositorio_producto.py  # Interfaz de repositorio
│   │
│   └── producto/                     # Repositorio concreto
│       ├── __init__.py
│       └── repositorio_producto_postgresql.py  # Implementacion PostgreSQL
│
├── database/                         # Scripts de base de datos
│   └── bdfacturas_postgres.sql       # Esquema completo de la BD
│
└── tutorial/                         # Documentacion del tutorial
    ├── Parte_1_Conceptos_Fundamentales.md
    ├── Parte_2_Crear_Proyecto_y_Configuracion.md
    ├── Parte_3_Capa_de_Datos.md
    ├── Parte_4_Capa_de_Negocio.md
    ├── Parte_5_Capa_de_Presentacion.md
    ├── Parte_6_Main_y_Ejecucion.md
    └── Parte_7_Flujo_Completo_y_Recapitulacion.md
```

---

## Conceptos Clave

### 1. Inversion de Dependencias (DIP - SOLID)

El proyecto sigue el **Principio de Inversion de Dependencias**:
- Los modulos de alto nivel no dependen de modulos de bajo nivel
- Ambos dependen de abstracciones (interfaces)
- Las abstracciones no dependen de detalles

```python
# El servicio depende de la abstraccion (IRepositorioProducto)
# No depende de la implementacion concreta (RepositorioProductoPostgreSQL)
class ServicioProducto:
    def __init__(self, repositorio):  # Inyeccion por constructor
        self._repo = repositorio
```

### 2. Patron Factory (Fabrica)

El patron Factory crea objetos sin especificar la clase exacta:

```python
def crear_servicio_producto() -> ServicioProducto:
    proveedor, nombre = _obtener_proveedor()  # Lee del .env
    repo = _crear_repo_entidad(_REPOS_PRODUCTO, proveedor, nombre)
    return ServicioProducto(repo)
```

### 3. Programacion Asincrona

El proyecto usa `async/await` para operaciones de base de datos:

```python
@router.get("/")
async def listar_productos():
    servicio = crear_servicio_producto()
    filas = await servicio.listar()  # No bloquea el servidor
    return filas
```

### 4. Duck Typing

Las interfaces (Protocol) permiten polimorfismo sin herencia:

```python
class IRepositorioProducto(Protocol):
    async def obtener_todos(self, ...) -> list[dict]: ...
    async def crear(self, ...) -> bool: ...
```

### 5. Validacion Automatica con Pydantic

Pydantic valida los datos automaticamente:

```python
class Producto(BaseModel):
    codigo: str                        # Obligatorio
    nombre: str                        # Obligatorio
    stock: int | None = None           # Opcional, valida tipo
    valorunitario: float | None = None # Opcional, valida tipo
```

### 6. Configuracion por Entornos

Soporte para multiples entornos (development, production):

```python
def get_env_file() -> str | tuple[str, str]:
    env = get_environment()
    if env == "development":
        return (".env", ".env.development")  # Sobrescribe valores
    return ".env"
```

---

## Tutorial Completo

El proyecto incluye un tutorial completo en español dividido en 7 partes:

| Parte | Titulo | Descripcion |
|-------|--------|-------------|
| 1 | Conceptos Fundamentales | Principios de APIs REST, FastAPI y arquitectura |
| 2 | Crear Proyecto y Configuracion | Setup del entorno, dependencias y configuracion |
| 3 | Capa de Datos | Repositorios, SQL y conexion a PostgreSQL |
| 4 | Capa de Negocio | Servicios, validaciones y logica de negocio |
| 5 | Capa de Presentacion | Controllers, routers y endpoints |
| 6 | Main y Ejecucion | Punto de entrada y configuracion de uvicorn |
| 7 | Flujo Completo y Recapitulacion | Integracion de todas las capas |

Para mas detalles, consulta los archivos en la carpeta [`tutorial/`](tutorial/).

---

## Contribuir

Este es un proyecto tutorial. Si encuentras errores o tienes sugerencias:

1. Revisa los archivos en [`tutorial/`](tutorial/) para entender el contexto
2. Verifica tu configuracion de base de datos en `.env`
3. Asegurate de tener todas las dependencias instaladas

---

## Licencia

Este proyecto es material educativo. Uso libre para fines de aprendizaje.

---

## Recursos Adicionales

- [Documentacion oficial de FastAPI](https://fastapi.tiangolo.com/)
- [Documentacion de Pydantic](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

<p align="center">
  <strong>Desarrollado con FastAPI</strong><br>
  Tutorial de APIs REST con arquitectura de 3 capas
</p>
