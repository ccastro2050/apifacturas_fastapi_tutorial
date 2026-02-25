# PARTE 2: Crear el Proyecto y Configuración

> En esta parte creamos el proyecto desde cero: directorio, Git, credenciales, entorno virtual, dependencias, variables de entorno, configuración centralizada, estructura de carpetas y la base de datos PostgreSQL.

> **Nota:** Si ya tienes experiencia con Git, entornos virtuales y configuración de proyectos Python, puedes ir directamente al **Resumen de Comandos y Archivos** al final de esta parte, donde están todos los comandos y contenidos de archivos de forma compacta.

---

## 2.1 Crear el Directorio del Proyecto e Inicializar Git

Abre una terminal (CMD, PowerShell o la terminal integrada de VS Code) y ejecuta:

```bash
# Crear la carpeta del proyecto
# mkdir = make directory (crear directorio)
mkdir apifacturas_fastapi_tutorial

# Entrar al directorio recién creado
# cd = change directory (cambiar de directorio)
cd apifacturas_fastapi_tutorial

# Inicializar un repositorio Git vacío
# Esto crea una carpeta oculta .git/ que almacena todo el historial de cambios
git init
```

**Salida esperada de `git init`:**
```
Initialized empty Git repository in .../apifacturas_fastapi_tutorial/.git/
```

**¿Qué es Git?** Es un sistema de control de versiones. Registra cada cambio que haces en el código. Si algo se rompe, puedes volver a una versión anterior. Si trabajas en equipo, cada persona puede trabajar en su rama sin interferir con los demás.

---

## 2.2 Verificar Configuración de GitHub en Windows

Antes de conectar con GitHub, hay que asegurarse de que las credenciales almacenadas en Windows sean correctas. Esto evita errores al hacer `git push`.

### 2.2.1 Abrir el Administrador de Credenciales

1. Presiona la tecla **Windows** y escribe: **Administrador de credenciales**
2. Haz clic en la aplicación que aparece con ese nombre

### 2.2.2 Ir a "Credenciales de Windows"

- Dentro del Administrador de credenciales, selecciona la pestaña **Credenciales de Windows**

### 2.2.3 Buscar Credenciales de GitHub

- En la lista, busca entradas que digan:
  - `github.com`
  - o `git:https://github.com`

### 2.2.4 Verificar Usuario

- Haz clic en la entrada de `github.com`
- Ahí se mostrará el **usuario** (si es tu cuenta, está bien)
- Si ves que pertenece a otra persona, deberás quitarla

### 2.2.5 Quitar Credenciales Incorrectas (si aplica)

- Selecciona la entrada
- Pulsa el botón **Quitar**
- Repite si hay varias entradas que no son tuyas

**Resultado esperado:** Tu Windows está libre de credenciales antiguas de GitHub. La próxima vez que uses `git push`, Git te pedirá usuario y contraseña/token.

---

## 2.3 Configurar Nombre y Correo en Git

Git necesita saber tu nombre y correo para **firmar cada commit** que hagas. El correo debe coincidir con el que usas en GitHub.

### 2.3.1 Configurar Variables Globales

En la terminal de VS Code, escribe (cambia por tus datos reales):

```bash
# Configurar tu nombre (aparecerá en cada commit)
git config --global user.name "Tu Nombre"

# Configurar tu correo (debe coincidir con tu cuenta de GitHub)
git config --global user.email "tu_correo@ejemplo.com"
```

**Ejemplo:**

```bash
git config --global user.name "Carlos Castro"
git config --global user.email "carlosarturo.castrocastro@gmail.com"
```

### 2.3.2 Verificar Configuración

Revisa que quedó guardado:

```bash
# Mostrar el nombre configurado
git config user.name

# Mostrar el correo configurado
git config user.email
```

**Esperado:** Debe mostrar el nombre y correo que configuraste.

### 2.3.3 Nota Importante

- Si pones `--global`, la configuración aplica a **todos los proyectos** en tu PC
- Si prefieres que solo aplique a **un proyecto específico**, quita el `--global`:

```bash
# Solo para este proyecto (sin --global)
git config user.name "Carlos Castro"
git config user.email "carlosarturo.castrocastro@gmail.com"
```

---

## 2.4 Qué Hacer Cuando Te Equivocas con un Comando Git

Equivocarse con Git es **completamente normal**, especialmente al principio. Lo importante es saber cómo corregir cada situación. Aquí están los errores más comunes y cómo solucionarlos.

### 2.4.1 Me equivoqué al escribir un comando (no se ejecutó)

Si escribiste mal un comando y Git muestra un error, simplemente **vuelve a escribirlo correctamente**. No pasó nada malo porque el comando no se ejecutó.

```bash
# ERROR: escribiste "git statsu" en vez de "git status"
git statsu
# Git dice: git: 'statsu' is not a git command. Did you mean 'status'?

# SOLUCIÓN: simplemente vuelve a escribirlo bien
git status
```

**Regla:** Si Git muestra un error y no ejecutó nada, solo reescribe el comando. No hay nada que deshacer.

---

### 2.4.2 Hice `git add` de un archivo que no quería agregar

Si agregaste un archivo al área de staging (zona de preparación) por error:

```bash
# Situación: agregaste todo sin querer
git add .

# Ver qué archivos están en staging
git status
# Muestra: Changes to be staged: .env, config.py, etc.

# SOLUCIÓN: quitar UN archivo específico del staging
# El archivo NO se borra, solo se quita de la zona de preparación
git reset HEAD .env

# SOLUCIÓN: quitar TODOS los archivos del staging
git reset HEAD
```

**¿Se pierde el archivo?** No. `git reset HEAD` solo quita el archivo del staging. El archivo sigue existiendo en tu carpeta, intacto.

---

### 2.4.3 Hice un commit con un mensaje equivocado (ANTES de hacer push)

Si hiciste commit pero el mensaje tiene un error y **todavía NO hiciste push**:

```bash
# Situación: hiciste commit con un mensaje incorrecto
git commit -m "agegar configuracion"
# El mensaje tiene un typo: "agegar" en vez de "agregar"

# SOLUCIÓN: corregir el mensaje del ÚLTIMO commit
# --amend = enmendar/corregir el commit anterior
git commit --amend -m "agregar configuración inicial del proyecto"
```

**Importante:** `--amend` **reemplaza** el último commit. Solo úsalo cuando **NO has hecho push todavía**. Si ya hiciste push, ve a la sección 2.4.4.

---

### 2.4.4 Hice un commit con mensaje equivocado Y ya hice push

Esta es la situación más delicada. El commit equivocado ya está en GitHub. Tienes dos opciones:

**Opción A — Forzar la corrección (si trabajas solo):**

```bash
# Paso 1: Corregir el mensaje localmente
git commit --amend -m "agregar configuración inicial del proyecto"

# Paso 2: Forzar el push para sobrescribir el commit en GitHub
# --force reemplaza el historial remoto con tu historial local
git push --force
```

> **ADVERTENCIA:** `git push --force` sobrescribe el historial en GitHub. Si otra persona ya descargó el commit anterior, tendrá conflictos. **Solo usa --force si trabajas solo en la rama.**

**Opción B — Hacer un nuevo commit (si trabajas en equipo):**

Si trabajas con otras personas, es mejor **no reescribir el historial**. Simplemente haz un nuevo commit explicando la corrección:

```bash
# No corriges el anterior, simplemente haces uno nuevo que aclare
git commit --allow-empty -m "corrección: el commit anterior debía decir 'agregar configuración'"
git push
```

---

### 2.4.5 Hice commit de un archivo que no debía incluir (ejemplo: `.env`)

Si por error hiciste commit del archivo `.env` (con credenciales):

```bash
# Paso 1: Quitar el archivo del rastreo de Git (pero NO borrarlo del disco)
# --cached = solo quitar del rastreo, mantener el archivo físico
git rm --cached .env

# Paso 2: Asegurarte de que .gitignore tenga .env
# (Si no lo tiene, agregarlo ahora)

# Paso 3: Hacer commit de la corrección
git commit -m "quitar .env del rastreo (contiene credenciales)"

# Paso 4: Push
git push
```

**¿Y si el `.env` ya está en GitHub?** Aunque lo quites del rastreo, el archivo sigue visible en el historial de commits anteriores. Si las credenciales son reales, **cámbialas** (nueva contraseña de base de datos).

---

### 2.4.6 Quiero deshacer el último commit (pero conservar los cambios)

Si hiciste commit pero te arrepentiste y quieres volver a editar los archivos:

```bash
# Deshacer el último commit, pero mantener los archivos modificados
# --soft = los archivos quedan en staging (listos para commit de nuevo)
# HEAD~1 = "un commit atrás"
git reset --soft HEAD~1
```

Ahora tus archivos están exactamente como antes del commit, en el área de staging. Puedes editarlos y hacer un commit nuevo.

**Diferencia entre --soft y --mixed:**

| Comando | Los archivos quedan en... | Uso típico |
|---------|--------------------------|------------|
| `git reset --soft HEAD~1` | Staging (listos para commit) | Quieres rehacer el commit con cambios adicionales |
| `git reset --mixed HEAD~1` | Working directory (sin staging) | Quieres revisar los archivos antes de volver a agregarlos |

> **Nunca uses `git reset --hard` a menos que estés 100% seguro.** `--hard` **borra** los cambios de tus archivos. No hay forma fácil de recuperarlos.

---

### 2.4.7 Hice push de algo incorrecto y quiero revertir (sin reescribir historial)

Si ya hiciste push de un commit malo y quieres deshacerlo de forma segura (sin `--force`):

```bash
# git revert crea un NUEVO commit que deshace los cambios del commit anterior.
# No borra historial — agrega un commit nuevo que "anula" el anterior.
git revert HEAD

# Git abrirá un editor para el mensaje del revert.
# Guarda y cierra el editor.

# Luego haz push del commit de revert
git push
```

**¿Cuál es la diferencia entre `reset` y `revert`?**

| Comando | Qué hace | ¿Reescribe historial? | ¿Seguro en equipo? |
|---------|----------|----------------------|---------------------|
| `git reset` | Borra commits del historial local | Sí | No (necesita --force) |
| `git revert` | Crea un commit NUEVO que anula el anterior | No | Sí (seguro para push normal) |

---

### 2.4.8 Tabla resumen: Errores comunes y soluciones

| Situación | Comando de solución | ¿Se pierde algo? |
|-----------|--------------------|--------------------|
| Comando mal escrito | Volver a escribirlo bien | No |
| `git add` de archivo incorrecto | `git reset HEAD archivo` | No |
| Commit con mensaje mal (sin push) | `git commit --amend -m "mensaje correcto"` | No |
| Commit con mensaje mal (con push, solo) | `git commit --amend -m "..."` + `git push --force` | No (pero reescribe historial remoto) |
| Commit con mensaje mal (con push, equipo) | Nuevo commit aclaratorio | No |
| Commit de archivo sensible (.env) | `git rm --cached .env` + commit | No (pero cambiar credenciales) |
| Deshacer último commit (conservar archivos) | `git reset --soft HEAD~1` | No |
| Revertir push malo (sin reescribir) | `git revert HEAD` + push | No |

**Consejo general:** Antes de hacer `git push`, **siempre revisa** qué vas a subir:

```bash
# Ver qué archivos cambiaron
git status

# Ver los cambios línea por línea
git diff

# Ver el historial de commits recientes
git log --oneline -5
```

---

## 2.5 Crear el Archivo `.gitignore`

El archivo `.gitignore` le dice a Git **qué archivos NO debe rastrear**. Esto evita subir archivos innecesarios o peligrosos al repositorio.

Crea un archivo llamado `.gitignore` en la raíz del proyecto con este contenido:

```gitignore
# ── Entorno virtual ──────────────────────────────────────────
# La carpeta venv/ contiene las librerías instaladas con pip.
# NO se versiona porque cada desarrollador la crea localmente
# con: python -m venv venv && pip install -r requirements.txt
venv/

# ── Bytecode de Python ──────────────────────────────────────
# Python compila los .py a bytecode (.pyc) para ejecutarlos más rápido.
# Estos archivos se regeneran automáticamente, no necesitan versionarse.
__pycache__/
*.pyc

# ── Variables de entorno ────────────────────────────────────
# El archivo .env contiene credenciales de base de datos (usuario,
# contraseña, servidor). NUNCA debe subirse a GitHub porque cualquier
# persona podría ver tus credenciales.
.env
.env.development

# ── Archivos temporales de Office ───────────────────────────
# Cuando Word/Excel tiene un archivo abierto, crea un temporal
# que empieza con ~$. No tiene sentido versionarlos.
~$*

# ── IDE y editores ──────────────────────────────────────────
# Carpetas de configuración de editores. Cada desarrollador
# tiene su propia configuración de VS Code, PyCharm, etc.
.vscode/
.idea/
```

**¿Qué pasa si NO creas `.gitignore`?** Al hacer `git add .` subirías el entorno virtual (cientos de MB), las credenciales de tu base de datos (riesgo de seguridad) y archivos basura que no aportan nada.

---

## 2.6 Crear el Entorno Virtual

Un **entorno virtual** es una carpeta aislada que contiene su propia copia de Python y sus propias librerías. Esto evita conflictos entre proyectos que usan versiones diferentes de las mismas librerías.

```bash
# Crear el entorno virtual en una carpeta llamada "venv"
# python -m venv = ejecutar el módulo venv de Python
# El último "venv" es el nombre de la carpeta (puede ser cualquier nombre)
python -m venv venv
```

### Activar el entorno virtual

**En Windows (CMD):**
```bash
venv\Scripts\activate
```

**En Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**En Linux / Mac:**
```bash
source venv/bin/activate
```

**¿Cómo saber que está activo?** Verás `(venv)` al inicio de la línea en tu terminal:

```
(venv) C:\...\apifacturas_fastapi_tutorial>
```

**Importante:** Cada vez que abras una nueva terminal, debes activar el entorno virtual antes de trabajar en el proyecto.

---

## 2.6 Crear `requirements.txt`

Este archivo lista todas las dependencias (librerías externas) que el proyecto necesita. Cualquier desarrollador que clone el proyecto puede instalar todo con un solo comando.

Crea el archivo `requirements.txt` en la raíz del proyecto:

```txt
# ─────────────────────────────────────────────────────────────
# Framework web asíncrono para construir la API REST.
# FastAPI es el framework principal. Proporciona:
# - Decoradores para definir rutas (@router.get, @router.post)
# - Validación automática con Pydantic
# - Documentación Swagger UI generada automáticamente en /docs
# - Soporte nativo para async/await (alto rendimiento)
# ─────────────────────────────────────────────────────────────
fastapi>=0.100.0

# ─────────────────────────────────────────────────────────────
# Servidor ASGI que ejecuta la aplicación FastAPI.
# ASGI = Asynchronous Server Gateway Interface.
# uvicorn recibe peticiones HTTP y las pasa a FastAPI.
# [standard] incluye herramientas adicionales para mejor rendimiento.
# Es equivalente a Kestrel en ASP.NET o Tomcat en Java.
# Comando para ejecutar: uvicorn main:app --reload
# ─────────────────────────────────────────────────────────────
uvicorn[standard]>=0.22.0

# ─────────────────────────────────────────────────────────────
# Librería de validación de datos.
# Pydantic v2 valida automáticamente los datos que recibe la API.
# Ejemplo: si defines stock: int y envían "abc", Pydantic rechaza
# la petición con un error 422 (Unprocessable Entity) antes de que
# llegue a tu código.
# ─────────────────────────────────────────────────────────────
pydantic>=2.0.0

# ─────────────────────────────────────────────────────────────
# Extensión de Pydantic para leer configuración desde archivos .env.
# Permite crear clases Settings que cargan automáticamente las
# variables de entorno. Así no tienes que hacer os.getenv() manualmente.
# ─────────────────────────────────────────────────────────────
pydantic-settings>=2.0.0

# ─────────────────────────────────────────────────────────────
# Soporte alternativo para cargar archivos .env.
# Algunas versiones de pydantic-settings lo requieren internamente.
# ─────────────────────────────────────────────────────────────
python-dotenv>=1.0.0

# ─────────────────────────────────────────────────────────────
# Driver asíncrono para PostgreSQL.
# asyncpg es el driver más rápido para PostgreSQL en Python.
# Permite ejecutar queries sin bloquear el hilo principal,
# lo que significa que la API puede atender otras peticiones
# mientras espera la respuesta de la base de datos.
# ─────────────────────────────────────────────────────────────
asyncpg>=0.28.0

# ─────────────────────────────────────────────────────────────
# ORM asíncrono (usamos SOLO como query builder, NO como ORM).
# SQLAlchemy proporciona:
# - create_async_engine: crea el pool de conexiones
# - text(): permite escribir SQL crudo con parámetros seguros
# - AsyncEngine/AsyncConnection: manejo async de conexiones
# NO usamos el ORM (modelos declarativos). Solo usamos SQLAlchemy
# como constructor de queries SQL parametrizados.
# [asyncio] incluye el soporte para async/await.
# ─────────────────────────────────────────────────────────────
sqlalchemy[asyncio]>=2.0.0

# ─────────────────────────────────────────────────────────────
# Requerido internamente por SQLAlchemy para async.
# greenlet permite que SQLAlchemy maneje contextos asíncronos
# internamente. Se instala como dependencia técnica.
# ─────────────────────────────────────────────────────────────
greenlet>=3.0.0
```

### Instalar las dependencias

Con el entorno virtual activo, ejecuta:

```bash
# pip install -r = instalar todas las librerías listadas en el archivo
# -r = read (leer desde archivo)
pip install -r requirements.txt
```

**Salida esperada:** Verás líneas como `Successfully installed fastapi-0.115.0 uvicorn-0.30.0 ...`

### Verificar la instalación

```bash
# Mostrar todas las librerías instaladas y sus versiones
pip list
```

Deberías ver fastapi, uvicorn, pydantic, sqlalchemy, asyncpg y sus dependencias.

---

## 2.7 Crear el Archivo `.env`

El archivo `.env` contiene las **variables de entorno**: valores de configuración que cambian entre entornos (desarrollo, pruebas, producción) y que **no deben estar en el código fuente**.

Crea el archivo `.env` en la raíz del proyecto:

```env
# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DEL ENTORNO
# ═══════════════════════════════════════════════════════════════

# Entorno de ejecución: "development" o "production"
# En "development" se pueden cargar archivos .env adicionales
# (.env.development) que sobrescriben valores del .env principal.
# En "production" solo se lee este archivo .env.
ENVIRONMENT=development

# Activar modo debug: muestra logs más detallados en la consola.
# En producción debe ser false para no exponer información sensible.
DEBUG=true

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE BASE DE DATOS
# ═══════════════════════════════════════════════════════════════

# Proveedor de base de datos activo.
# Este valor determina cuál repositorio y cuál cadena de conexión usar.
# La fábrica (fabrica_repositorios.py) lee esta variable para decidir
# qué clase de repositorio instanciar.
# Opciones válidas: postgres, postgresql, sqlserver, mysql, mariadb
DB_PROVIDER=postgres

# Cadena de conexión para PostgreSQL.
#
# Formato: postgresql+asyncpg://usuario:contraseña@host:puerto/nombre_bd
#
# Desglose:
#   postgresql+asyncpg  → Indica que usamos el driver asyncpg con SQLAlchemy
#   postgres             → Usuario de PostgreSQL (por defecto es "postgres")
#   postgres             → Contraseña del usuario (cámbiala por la tuya)
#   localhost            → Servidor (tu máquina local)
#   5432                 → Puerto por defecto de PostgreSQL
#   bdfacturas_postgres_local → Nombre de la base de datos
#
# IMPORTANTE: Cambia "postgres:postgres" por tu usuario y contraseña reales.
DB_POSTGRES=postgresql+asyncpg://postgres:postgres@localhost:5432/bdfacturas_postgres_local
```

**¿Por qué `.env` y no hardcoded?**

| Enfoque | Ejemplo | Problema |
|---------|---------|----------|
| **Hardcoded (MAL)** | `engine = create_async_engine("postgresql+asyncpg://postgres:mi_password@localhost/midb")` | La contraseña queda en el código fuente. Si lo subes a GitHub, cualquiera la ve. |
| **Variable de entorno (BIEN)** | Se lee desde `.env` con `pydantic-settings` | La contraseña está en un archivo que `.gitignore` excluye. Nunca llega a GitHub. |

---

## 2.8 Crear `config.py` — Configuración Centralizada

Este archivo lee el `.env` y expone la configuración como objetos Python tipados. Usa `pydantic-settings` para validar automáticamente los valores.

Crea el archivo `config.py` en la raíz del proyecto:

```python
"""
config.py — Configuración centralizada usando pydantic-settings.

Lee variables desde archivos .env según el entorno:
- Production:  solo .env
- Development: .env + .env.development (sobrescribe valores)

Este archivo implementa el patrón SINGLETON con @lru_cache:
la configuración se lee del disco una sola vez y se reutiliza
en todas las llamadas posteriores.
"""

# ─── Imports ─────────────────────────────────────────────────

import os                       # Módulo estándar de Python para interactuar con el sistema operativo.
                                # Lo usamos para leer la variable de entorno ENVIRONMENT y
                                # verificar si existe el archivo .env.development.

from functools import lru_cache # lru_cache es un decorador que CACHEA el resultado de una función.
                                # La primera vez que llamas a la función, ejecuta el código y guarda
                                # el resultado. Las siguientes veces, retorna el resultado guardado
                                # sin ejecutar el código de nuevo. Esto implementa el patrón SINGLETON.

from pydantic import Field      # Field permite definir valores por defecto, aliases y validaciones
                                # para los campos de las clases Settings.

from pydantic_settings import BaseSettings, SettingsConfigDict
                                # BaseSettings: clase base que lee automáticamente variables de entorno.
                                # SettingsConfigDict: configuración de cómo leer los archivos .env
                                # (nombre del archivo, encoding, prefijo de variables, etc.).


# ═════════════════════════════════════════════════════════════
# DETECCIÓN DE ENTORNO
# ═════════════════════════════════════════════════════════════

def get_environment() -> str:
    """
    Detecta el entorno actual desde la variable ENVIRONMENT.

    Si ENVIRONMENT no está definida en el sistema, usa "production"
    como valor por defecto (lo más seguro para producción).
    .lower() convierte a minúsculas para evitar errores por mayúsculas.
    """
    return os.getenv("ENVIRONMENT", "production").lower()
    # os.getenv("ENVIRONMENT", "production")
    #   → Busca la variable ENVIRONMENT en el sistema operativo.
    #   → Si no existe, retorna "production" (valor por defecto seguro).
    # .lower()
    #   → Convierte a minúsculas: "Development" → "development".


def get_env_file() -> str | tuple[str, str]:
    """
    Retorna qué archivo(s) .env cargar según el entorno.

    En development: carga .env y luego .env.development.
    Los valores de .env.development sobrescriben los de .env.
    Esto permite tener configuraciones diferentes por entorno.

    En production: solo carga .env.
    """
    env = get_environment()             # Lee el entorno actual ("development" o "production")
    if env == "development":            # Si estamos en desarrollo...
        env_dev = ".env.development"    # Nombre del archivo de desarrollo
        if os.path.exists(env_dev):     # Solo si el archivo existe en disco
            return (".env", env_dev)    # Retorna AMBOS archivos como tupla
    return ".env"                       # En producción (o si no existe .env.development)


# ═════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE BASE DE DATOS
# ═════════════════════════════════════════════════════════════

class DatabaseSettings(BaseSettings):
    """
    Cadenas de conexión para cada proveedor de base de datos.

    BaseSettings lee automáticamente las variables de entorno que
    coincidan con los nombres de los campos (con el prefijo DB_).

    Ejemplo: el campo 'postgres' lee la variable DB_POSTGRES del .env.
    """

    model_config = SettingsConfigDict(
        env_file=get_env_file(),        # Qué archivo(s) .env leer
        env_file_encoding='utf-8',      # Encoding del archivo (soporta caracteres especiales)
        env_prefix='DB_',               # PREFIJO: solo lee variables que empiezan con DB_
                                        # Así, DB_PROVIDER se mapea al campo "provider",
                                        # DB_POSTGRES se mapea al campo "postgres", etc.
        extra='ignore'                  # Ignorar variables extra que no coincidan con campos
    )

    # Proveedor activo — determina qué repositorio y cadena de conexión usar.
    # Lee DB_PROVIDER del .env. Si no existe, usa "postgres" por defecto.
    provider: str = Field(default='postgres')

    # Cadenas de conexión por proveedor.
    # Cada campo lee su variable DB_ correspondiente del .env.
    # Si la variable no existe, usa string vacío como valor por defecto.
    postgres: str = Field(default='')       # Lee DB_POSTGRES


# ═════════════════════════════════════════════════════════════
# CONFIGURACIÓN PRINCIPAL
# ═════════════════════════════════════════════════════════════

class Settings(BaseSettings):
    """
    Agrupa toda la configuración de la aplicación.

    Esta clase es el punto de entrada para acceder a cualquier
    configuración. Contiene configuraciones generales (debug, environment)
    y una instancia de DatabaseSettings para las cadenas de conexión.
    """

    model_config = SettingsConfigDict(
        env_file=get_env_file(),        # Mismos archivos .env que DatabaseSettings
        env_file_encoding='utf-8',      # Mismo encoding
        extra='ignore'                  # Ignorar variables extra
    )

    # Campo debug: lee la variable DEBUG del .env.
    # alias='DEBUG' permite que el campo en Python sea minúscula (debug)
    # pero lea la variable en mayúscula (DEBUG) del .env.
    debug: bool = Field(default=False, alias='DEBUG')

    # Campo environment: usa la función get_environment() como valor por defecto.
    # default_factory significa: "llama a esta función para obtener el valor".
    environment: str = Field(default_factory=get_environment)

    # Campo database: crea una instancia de DatabaseSettings.
    # default_factory=DatabaseSettings significa: "crea un DatabaseSettings nuevo".
    # Esto lee automáticamente todas las variables DB_* del .env.
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)


# ═════════════════════════════════════════════════════════════
# SINGLETON (se crea una sola vez y se reutiliza)
# ═════════════════════════════════════════════════════════════

@lru_cache()    # ← PATRÓN SINGLETON.
                # La primera vez que alguien llama a get_settings():
                #   1. Crea un objeto Settings() (lee el .env del disco)
                #   2. Lo guarda en memoria (cache)
                #   3. Lo retorna
                # Las siguientes veces:
                #   1. Retorna el objeto guardado SIN leer el disco de nuevo
                # Resultado: el .env se lee UNA SOLA VEZ en toda la vida de la app.
def get_settings() -> Settings:
    """Obtiene la configuración cacheada (singleton)."""
    return Settings()
```

### ¿Cómo se usa `config.py`?

Desde cualquier parte del proyecto:

```python
from config import get_settings

settings = get_settings()                           # Singleton: siempre el mismo objeto
print(settings.database.provider)                   # "postgres"
print(settings.database.postgres)                   # "postgresql+asyncpg://postgres:..."
print(settings.debug)                               # True
print(settings.environment)                         # "development"
```

---

## 2.9 Crear la Estructura de Carpetas

Ahora creamos todos los directorios y archivos `__init__.py` necesarios.

### Crear los directorios

```bash
# Crear las carpetas principales (una por capa)
mkdir models                        # Modelos Pydantic (validación de datos)
mkdir controllers                   # Capa de presentación (endpoints HTTP)
mkdir servicios                     # Capa de negocio (lógica y validaciones)
mkdir repositorios                  # Capa de datos (acceso a base de datos)
mkdir database                      # Scripts SQL

# Crear subcarpetas dentro de servicios
mkdir servicios\abstracciones       # Interfaces (Protocols) de la capa de negocio
mkdir servicios\conexion            # Proveedor de conexión a base de datos

# Crear subcarpetas dentro de repositorios
mkdir repositorios\abstracciones    # Interfaces (Protocols) de la capa de datos
mkdir repositorios\producto         # Repositorio específico de producto
```

> **Nota Linux/Mac:** Reemplaza `\` por `/` en las rutas.

### Crear los archivos `__init__.py`

En Python, una carpeta se convierte en un **paquete** (importable) solo si contiene un archivo `__init__.py`. Sin este archivo, Python no puede hacer `from models.producto import Producto`.

Crea un archivo `__init__.py` **vacío** en cada carpeta:

```
models/__init__.py
controllers/__init__.py
servicios/__init__.py
servicios/abstracciones/__init__.py
servicios/conexion/__init__.py
repositorios/__init__.py
repositorios/abstracciones/__init__.py
repositorios/producto/__init__.py
```

Puedes crearlos rápidamente desde la terminal:

```bash
# Crear todos los __init__.py vacíos
# echo. > archivo crea un archivo vacío en Windows
echo. > models\__init__.py
echo. > controllers\__init__.py
echo. > servicios\__init__.py
echo. > servicios\abstracciones\__init__.py
echo. > servicios\conexion\__init__.py
echo. > repositorios\__init__.py
echo. > repositorios\abstracciones\__init__.py
echo. > repositorios\producto\__init__.py
```

**Estructura resultante hasta ahora:**

```
apifacturas_fastapi_tutorial/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
├── models/
│   └── __init__.py
├── controllers/
│   └── __init__.py
├── servicios/
│   ├── __init__.py
│   ├── abstracciones/
│   │   └── __init__.py
│   └── conexion/
│       └── __init__.py
├── repositorios/
│   ├── __init__.py
│   ├── abstracciones/
│   │   └── __init__.py
│   └── producto/
│       └── __init__.py
└── database/
```

---

## 2.11 La Base de Datos PostgreSQL

### 2.11.1 Proceso de diseño (ya realizado)

La base de datos `bdfacturas_postgres` ya pasó por las **3 etapas del diseño de bases de datos**:

| Etapa | Qué se hizo | Resultado |
|-------|-------------|-----------|
| **1. Diseño Conceptual (MER)** | Se identificaron las entidades del negocio (persona, empresa, cliente, vendedor, producto, factura, usuario, rol, ruta) y sus relaciones. Se creó el Modelo Entidad-Relación. | Diagrama ER con cardinalidades (1:N, N:M) |
| **2. Diseño Lógico (Normalización)** | Se normalizó hasta la 3ra Forma Normal (3FN): sin datos repetidos, sin dependencias parciales, sin dependencias transitivas. Las relaciones N:M se resolvieron con tablas intermedias (ej: `productosporfactura`, `rol_usuario`, `rutarol`). | 12 tablas normalizadas |
| **3. Diseño Físico (PostgreSQL)** | Se implementó en PostgreSQL: tipos de datos, constraints (PK, FK, CHECK, UNIQUE), trigger para cálculos automáticos, stored procedures para operaciones maestro-detalle, y datos de ejemplo. | Script SQL de 1133 líneas |

> **Nota:** En este tutorial nos enfocamos en la **tabla `producto`**, pero la base de datos completa incluye todas las entidades del sistema de facturación.

### 2.11.2 Descripción de la base de datos completa

El script `database/bdfacturas_postgres.sql` (incluido en el proyecto) contiene **7 secciones**:

**Sección 1 — Tablas independientes (sin FK):**

| Tabla | PK | Descripción |
|-------|-----|-------------|
| `persona` | `codigo` (VARCHAR) | Personas naturales (nombre, email, teléfono) |
| `empresa` | `codigo` (VARCHAR) | Personas jurídicas (nombre) |
| `producto` | `codigo` (VARCHAR) | Catálogo de productos (nombre, stock, precio) — **Esta es nuestra tabla del tutorial** |
| `usuario` | `email` (VARCHAR) | Usuarios del sistema (contraseña encriptada con BCrypt) |
| `rol` | `id` (SERIAL) | Roles del sistema (admin, vendedor, etc.) |
| `ruta` | `ruta` (VARCHAR) | Endpoints protegidos del sistema |

**Sección 2 — Tablas con FK (relaciones):**

| Tabla | PK | FK apunta a | Relación |
|-------|-----|-------------|----------|
| `cliente` | `id` (SERIAL) | `persona` o `empresa` | Un cliente es una persona o una empresa |
| `vendedor` | `id` (SERIAL) | `persona` | Un vendedor es una persona |
| `factura` | `numero` (SERIAL) | `cliente`, `vendedor` | Cada factura tiene un cliente y un vendedor |
| `productosporfactura` | `fknumfactura` + `fkcodigoproducto` | `factura`, `producto` | Detalle: qué productos tiene cada factura |
| `rol_usuario` | `fkemail` + `fkidrol` | `usuario`, `rol` | Qué roles tiene cada usuario |
| `rutarol` | `fkruta` + `fkidrol` | `ruta`, `rol` | Qué roles pueden acceder a cada ruta |

**Sección 3 — Trigger automático:**

La función `actualizar_totales_y_stock()` se ejecuta automáticamente al insertar un detalle en `productosporfactura`. Calcula el subtotal (cantidad × precio), actualiza el total de la factura y descuenta el stock del producto.

**Sección 4 — 20 Stored Procedures:**

Operaciones maestro-detalle CRUD para las relaciones complejas: crear persona con cliente, crear factura con productos, crear usuario con roles, etc. Cada entidad maestro-detalle tiene 4 SP (crear, obtener, actualizar, eliminar).

**Sección 5 — Datos de ejemplo** para todas las tablas.

**Sección 6 — Ejemplos de uso (CALL)** de los 20 stored procedures.

**Sección 7 — Ajuste de secuencias** para que los SERIAL continúen después de los datos de ejemplo.

### 2.11.3 La tabla `producto` (nuestro enfoque)

De toda la base de datos, en este tutorial trabajamos solo con la tabla `producto`:

```sql
CREATE TABLE producto (
    codigo          VARCHAR(30)    NOT NULL,     -- PK: identificador único ('PR001', 'PR002')
    nombre          VARCHAR(100)   NOT NULL,     -- Nombre descriptivo del producto
    stock           INTEGER        NOT NULL,     -- Cantidad disponible en inventario
    valorunitario   NUMERIC(14,2)  NOT NULL,     -- Precio por unidad (14 dígitos, 2 decimales)
    CONSTRAINT producto_pkey PRIMARY KEY (codigo),
    CONSTRAINT producto_stock_check          CHECK (stock >= 0),         -- Stock no negativo
    CONSTRAINT producto_valorunitario_check  CHECK (valorunitario >= 0)  -- Precio no negativo
);
```

**Datos de ejemplo incluidos en el script:**

| codigo | nombre | stock | valorunitario |
|--------|--------|-------|---------------|
| PR001 | Laptop Lenovo IdeaPad | 20 | 2,500,000.00 |
| PR002 | Monitor Samsung 24" | 30 | 800,000.00 |
| PR003 | Teclado Logitech K380 | 50 | 150,000.00 |
| PR004 | Mouse HP X200 | 60 | 90,000.00 |
| PR005 | Impresora Epson EcoTank | 15 | 1,100,000.00 |

### 2.11.4 Crear la base de datos y ejecutar el script

Primero, crea la base de datos vacía. Luego ejecuta el script completo.

**Paso 1 — Crear la base de datos vacía:**

Puedes usar cualquiera de estas opciones:

**Opción A — Desde pgAdmin (interfaz gráfica):**
1. Abre pgAdmin → conecta a tu servidor PostgreSQL
2. Clic derecho en **Databases** → **Create** → **Database...**
3. Escribe el nombre: `bdfacturas_postgres_local`
4. Clic en **Save**

**Opción B — Desde la terminal psql:**
```bash
# Conectar a PostgreSQL como usuario postgres
psql -U postgres

# Dentro de psql, crear la base de datos
CREATE DATABASE bdfacturas_postgres_local;

# Salir de psql
\q
```

**Opción C — Desde DBeaver:**
1. Conecta a tu servidor PostgreSQL
2. Clic derecho en **Databases** → **Create New Database**
3. Nombre: `bdfacturas_postgres_local` → **OK**

**Opción D — Desde la terminal del sistema operativo (una línea):**
```bash
# createdb es una utilidad de PostgreSQL que crea bases de datos
createdb -U postgres bdfacturas_postgres_local
```

---

**Paso 2 — Ejecutar el script SQL:**

El archivo `database/bdfacturas_postgres.sql` ya está incluido en el proyecto. Ejecútalo sobre la base de datos recién creada:

**Opción A — Desde pgAdmin:**
1. Selecciona la base de datos `bdfacturas_postgres_local` en el árbol
2. Abre el **Query Tool** (menú Tools → Query Tool, o clic derecho → Query Tool)
3. Abre el archivo: File → Open → busca `database/bdfacturas_postgres.sql`
4. Ejecuta todo con **F5** o el botón **Play** (▶)

**Opción B — Desde terminal psql:**
```bash
# -U postgres = usuario
# -d bdfacturas_postgres_local = base de datos destino
# -f database/bdfacturas_postgres.sql = archivo a ejecutar
psql -U postgres -d bdfacturas_postgres_local -f database/bdfacturas_postgres.sql
```

**Opción C — Desde DBeaver:**
1. Conecta a `bdfacturas_postgres_local`
2. Abre un nuevo SQL Editor
3. Pega o abre el contenido del archivo
4. Ejecuta todo (Ctrl+Enter o botón de ejecutar)

### 2.11.5 Verificar la instalación

Ejecuta esta consulta para confirmar que todo se creó correctamente:

```sql
-- Verificar que la tabla producto existe y tiene datos
SELECT * FROM producto ORDER BY codigo;
```

**Resultado esperado:**

```
 codigo |         nombre           | stock | valorunitario
--------+--------------------------+-------+--------------
 PR001  | Laptop Lenovo IdeaPad    |    20 |   2500000.00
 PR002  | Monitor Samsung 24"      |    30 |    800000.00
 PR003  | Teclado Logitech K380    |    50 |    150000.00
 PR004  | Mouse HP X200            |    60 |     90000.00
 PR005  | Impresora Epson EcoTank  |    15 |   1100000.00
```

Si ves las 5 filas, la base de datos está lista.

---

## Resumen de la Parte 2

### Secciones cubiertas

| # | Acción | Archivo/Comando |
|---|--------|----------------|
| 2.1 | Crear proyecto y git init | `mkdir` + `git init` |
| 2.2 | Verificar credenciales GitHub | Administrador de credenciales Windows |
| 2.3 | Configurar nombre/correo Git | `git config --global` |
| 2.4 | Corregir errores en Git | `--amend`, `reset`, `revert`, `rm --cached` |
| 2.5 | Crear `.gitignore` | `.gitignore` (5 reglas) |
| 2.6 | Crear entorno virtual | `python -m venv venv` |
| 2.7 | Crear dependencias | `requirements.txt` (8 paquetes) |
| 2.8 | Crear variables de entorno | `.env` (4 variables) |
| 2.9 | Crear configuración | `config.py` (~88 líneas, patrón Singleton) |
| 2.10 | Crear estructura de carpetas | 8 directorios + 8 `__init__.py` |
| 2.11 | Base de datos PostgreSQL | `database/bdfacturas_postgres.sql` (1133 líneas, 12 tablas) |

### Resumen completo: comandos, archivos y código

**1. Crear proyecto e inicializar Git:**

```bash
mkdir apifacturas_fastapi_tutorial          # Crear la carpeta del proyecto
cd apifacturas_fastapi_tutorial             # Entrar al directorio
git init                                    # Inicializar repositorio Git
```

**2. Configurar Git:**

```bash
git config --global user.name "Tu Nombre"   # Nombre que aparece en los commits
git config --global user.email "tu@email"   # Correo asociado a tu cuenta GitHub
```

**3. Archivo `.gitignore`:**

```gitignore
venv/                # Entorno virtual (no se versiona)
__pycache__/         # Bytecode compilado por Python
*.pyc                # Archivos individuales de bytecode
.env                 # Variables de entorno con credenciales
.env.development     # Variables de entorno de desarrollo
~$*                  # Archivos temporales de Office
.vscode/             # Configuración de VS Code
.idea/               # Configuración de PyCharm
```

**4. Crear entorno virtual y activar:**

```bash
python -m venv venv                         # Crear entorno virtual aislado
venv\Scripts\activate                       # Activar (Windows CMD)
venv\Scripts\Activate.ps1                   # Activar (Windows PowerShell)
source venv/bin/activate                    # Activar (Linux/Mac)
```

**5. Archivo `requirements.txt` e instalar:**

```txt
fastapi>=0.100.0              # Framework web asíncrono (endpoints, Swagger UI)
uvicorn[standard]>=0.22.0     # Servidor ASGI que ejecuta FastAPI
pydantic>=2.0.0               # Validación automática de datos de entrada
pydantic-settings>=2.0.0      # Leer configuración desde archivos .env
python-dotenv>=1.0.0          # Soporte para cargar .env
asyncpg>=0.28.0               # Driver asíncrono para PostgreSQL
sqlalchemy[asyncio]>=2.0.0    # Query builder SQL (NO usamos ORM)
greenlet>=3.0.0               # Requerido internamente por SQLAlchemy async
```

```bash
pip install -r requirements.txt             # Instalar las 8 librerías
pip list                                    # Verificar instalación
```

**6. Archivo `.env`:**

```env
ENVIRONMENT=development                     # Entorno de ejecución
DEBUG=true                                  # Modo debug activado
DB_PROVIDER=postgres                        # Motor de BD activo
DB_POSTGRES=postgresql+asyncpg://postgres:postgres@localhost:5432/bdfacturas_postgres_local
```

**7. Archivo `config.py`** (ver sección 2.9 para código completo con comentarios):

```python
# Lee .env con pydantic-settings → DatabaseSettings (cadenas de conexión)
#                                → Settings (debug, environment, database)
# @lru_cache en get_settings() → patrón Singleton (se lee una sola vez)
```

**8. Crear estructura de carpetas:**

```bash
mkdir models controllers servicios repositorios database
mkdir servicios\abstracciones servicios\conexion
mkdir repositorios\abstracciones repositorios\producto
```

**9. Crear archivos `__init__.py` (paquetes Python):**

```bash
echo. > models\__init__.py                  # Hace que models/ sea importable
echo. > controllers\__init__.py             # Hace que controllers/ sea importable
echo. > servicios\__init__.py               # Hace que servicios/ sea importable
echo. > servicios\abstracciones\__init__.py # Hace que abstracciones/ sea importable
echo. > servicios\conexion\__init__.py      # Hace que conexion/ sea importable
echo. > repositorios\__init__.py            # Hace que repositorios/ sea importable
echo. > repositorios\abstracciones\__init__.py  # Hace que abstracciones/ sea importable
echo. > repositorios\producto\__init__.py   # Hace que producto/ sea importable
```

**10. Base de datos PostgreSQL (pgAdmin):**

1. Abrir **pgAdmin** → conectar a tu servidor PostgreSQL
2. Clic derecho en **Databases** → **Create** → **Database...**
3. Nombre: `bdfacturas_postgres_local` → **Save**
4. Seleccionar la base de datos recién creada en el árbol
5. Abrir **Query Tool** (menú Tools → Query Tool)
6. Abrir archivo: **File → Open** → buscar `database/bdfacturas_postgres.sql`
7. Ejecutar todo con **F5** o botón **Play** (▶)
8. Verificar: ejecutar `SELECT * FROM producto ORDER BY codigo;` → debe mostrar 5 filas

**11. Referencia rápida — Corregir errores en Git:**

| Situación | Comando | Qué hace |
|-----------|---------|----------|
| Ver estado | `git status` | Muestra archivos modificados y en staging |
| Ver cambios | `git diff` | Muestra diferencias línea por línea |
| Ver historial | `git log --oneline -5` | Últimos 5 commits en una línea |
| Quitar del staging | `git reset HEAD archivo` | Saca archivo de staging, no lo borra |
| Corregir mensaje (sin push) | `git commit --amend -m "nuevo"` | Reemplaza el último commit |
| Forzar push tras amend | `git push --force` | Solo si trabajas solo en la rama |
| Dejar de rastrear archivo | `git rm --cached archivo` | Quita del repo, mantiene en disco |
| Deshacer último commit | `git reset --soft HEAD~1` | Conserva archivos en staging |
| Revertir commit (seguro) | `git revert HEAD` | Crea commit nuevo que anula el anterior |

---

## Siguiente paso

En la **Parte 3** construiremos la **capa de datos**: las interfaces (Protocols), el proveedor de conexión, el repositorio base de PostgreSQL (~380 líneas) y el repositorio específico de producto. Es la capa más densa del proyecto.

---

> **Nota:** Al terminar esta parte, aún no puedes ejecutar la API (no hay `main.py` ni controllers). Pero ya tienes toda la infraestructura de configuración lista. A partir de la Parte 3, cada archivo que crees será código funcional.
