"""
base_repositorio_postgresql.py — Clase base con lógica SQL para PostgreSQL.

Características de PostgreSQL:
- Identificadores con "comillas dobles"
- LIMIT n para limitar resultados
- Esquema por defecto: 'public'
"""

from typing import Any                # Any: tipo comodín, acepta cualquier tipo.
from datetime import datetime, date, time  # Tipos de fecha/hora de Python.
from decimal import Decimal           # Números con precisión exacta (para valores monetarios).
from uuid import UUID                 # Identificador universal único de 128 bits.

from sqlalchemy import text           # text(): escribir SQL crudo con parámetros seguros (:param).
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
                                      # create_async_engine: crea pool de conexiones asíncronas.
                                      # AsyncEngine: tipo del objeto engine (para type hints).

from servicios.abstracciones.i_proveedor_conexion import IProveedorConexion
# Depende de la ABSTRACCIÓN (interfaz), no de la implementación concreta.
# Esto cumple el principio D de SOLID (Inversión de Dependencias).


class BaseRepositorioPostgreSQL:
    """Clase base con la lógica SQL de PostgreSQL. Los repositorios específicos heredan de esta clase."""
    # Clase abstracta en la práctica: no se usa directamente, siempre a través de subclases.
    # Los métodos protegidos (_prefijo) solo son llamados por las subclases.

    def __init__(self, proveedor_conexion: IProveedorConexion):
        if proveedor_conexion is None:                     # Validación: fail fast si es None
            raise ValueError("proveedor_conexion no puede ser None")
        self._proveedor_conexion = proveedor_conexion      # Guarda referencia (atributo privado)
        self._engine: AsyncEngine | None = None            # Engine: se crea lazy (primera vez que se necesita)

    async def _obtener_engine(self) -> AsyncEngine:
        """Crea el engine de conexión la primera vez, luego lo reutiliza."""
        if self._engine is None:                           # LAZY LOADING: solo la primera vez
            cadena = self._proveedor_conexion.obtener_cadena_conexion()  # Obtiene cadena del .env
            self._engine = create_async_engine(cadena, echo=False)      # Crea pool de conexiones
                                                           # echo=False: no imprime SQL en consola
        return self._engine                                # Retorna el engine (nuevo o existente)

    # ================================================================
    # MÉTODOS AUXILIARES — Detección y conversión de tipos
    # ================================================================

    async def _detectar_tipo_columna(
        self, nombre_tabla: str, esquema: str, nombre_columna: str
    ) -> str | None:
        """Consulta information_schema para saber el tipo de una columna."""
        # information_schema.columns: vista del sistema con metadatos de todas las columnas.
        sql = text("""
            SELECT data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema = :esquema
            AND table_name = :tabla
            AND column_name = :columna
        """)
        # Los :parámetros son seguros (previenen SQL injection).
        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:           # Obtiene conexión del pool
                result = await conn.execute(sql, {         # Ejecuta con parámetros seguros
                    "esquema": esquema, "tabla": nombre_tabla,
                    "columna": nombre_columna
                })
                row = result.fetchone()                    # Primera fila del resultado
                return row[0].lower() if row else None     # Tipo en minúsculas o None
        except Exception:
            return None                                    # Si falla, retorna None (se usará str)

    def _convertir_valor(self, valor: str, tipo_destino: str | None) -> Any:
        """Convierte un string al tipo Python que corresponde."""
        # JSON siempre envía strings. La BD espera tipos específicos.
        # Ej: "20" → int(20), "50000.00" → Decimal("50000.00")
        if tipo_destino is None:
            return valor                                   # Sin tipo detectado: queda como string
        try:
            if tipo_destino in ('integer', 'int4', 'bigint', 'int8',
                                'smallint', 'int2'):
                return int(valor)                          # "20" → 20
            if tipo_destino in ('numeric', 'decimal'):
                return Decimal(valor)                      # "50000.00" → Decimal('50000.00')
            if tipo_destino in ('real', 'float4', 'double precision', 'float8'):
                return float(valor)                        # "3.14" → 3.14
            if tipo_destino in ('boolean', 'bool'):
                return valor.lower() in ('true', '1', 'yes', 'si', 't')  # "true" → True
            if tipo_destino == 'uuid':
                return UUID(valor)                         # "550e8400-..." → UUID object
            if tipo_destino == 'date':
                return self._extraer_solo_fecha(valor)     # "2024-01-15" → date object
            if tipo_destino in ('timestamp without time zone',
                                'timestamp with time zone'):
                return datetime.fromisoformat(valor.replace('Z', '+00:00'))  # ISO → datetime
            if tipo_destino == 'time':
                return time.fromisoformat(valor)           # "14:30:00" → time object
            return valor                                   # Tipo no reconocido: queda como string
        except (ValueError, TypeError):
            return valor                                   # Si la conversión falla: queda como string

    def _extraer_solo_fecha(self, valor: str) -> date:
        """Extrae la parte de fecha de un string ISO."""
        if 'T' in valor:                                   # Tiene hora: "2024-01-15T14:30:00"
            return datetime.fromisoformat(
                valor.replace('Z', '+00:00')               # Convierte UTC JavaScript a ISO Python
            ).date()                                       # Extrae solo la fecha
        return date.fromisoformat(valor[:10])              # Solo fecha: "2024-01-15"

    def _es_fecha_sin_hora(self, valor: str) -> bool:
        """Detecta si un valor tiene formato YYYY-MM-DD (solo fecha)."""
        return (len(valor) == 10 and valor.count('-') == 2
                and 'T' not in valor)
    # 10 caracteres, 2 guiones, sin 'T': "2024-01-15" → True

    def _serializar_valor(self, valor: Any) -> Any:
        """Convierte tipos Python a tipos serializables para JSON."""
        # JSON no tiene tipos nativos para fecha, Decimal o UUID.
        if isinstance(valor, (datetime, date)):
            return valor.isoformat()                       # datetime/date → "2024-01-15T00:00:00"
        elif isinstance(valor, Decimal):
            return float(valor)                            # Decimal('2500000.00') → 2500000.0
        elif isinstance(valor, UUID):
            return str(valor)                              # UUID → "550e8400-e29b-..."
        return valor                                       # str, int, float: sin cambio

    # ================================================================
    # OPERACIÓN 1: LISTAR (SELECT * LIMIT n)
    # ================================================================

    async def _obtener_filas(
        self, nombre_tabla: str, esquema: str | None = None,
        limite: int | None = None
    ) -> list[dict[str, Any]]:
        """Obtiene filas de una tabla con LIMIT opcional."""
        if not nombre_tabla or not nombre_tabla.strip():   # Validación: tabla obligatoria
            raise ValueError("El nombre de la tabla no puede estar vacío")

        esquema_final = (esquema or "public").strip()      # Default "public" si es None
        limite_final = limite or 1000                      # Default 1000 si es None o 0

        sql = text(
            f'SELECT * FROM "{esquema_final}"."{nombre_tabla}" LIMIT :limite'
        )
        # "comillas dobles": sintaxis PostgreSQL para identificadores.
        # :limite es parámetro seguro (previene SQL injection).

        try:
            engine = await self._obtener_engine()          # Pool de conexiones (lazy)
            async with engine.connect() as conn:           # Obtiene conexión, la libera al salir
                result = await conn.execute(sql, {"limite": limite_final})  # await: no bloquea
                columnas = result.keys()                   # ["codigo", "nombre", "stock", ...]
                return [
                    {col: self._serializar_valor(row[i])   # Serializa cada valor para JSON
                     for i, col in enumerate(columnas)}    # Dict comprehension por fila
                    for row in result.fetchall()            # List comprehension de todas las filas
                ]
                # Cada fila tupla → diccionario: ("PR001", "Laptop", 20) → {"codigo": "PR001", ...}
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al consultar "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex                                      # "from ex" conserva error original

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
        if not nombre_clave or not nombre_clave.strip():   # nombre_clave: columna PK (ej: "codigo")
            raise ValueError("El nombre de la clave no puede estar vacío")
        if not valor or not valor.strip():                 # valor: valor a buscar (ej: "PR001")
            raise ValueError("El valor no puede estar vacío")

        esquema_final = (esquema or "public").strip()

        try:
            tipo_columna = await self._detectar_tipo_columna(  # Consulta metadatos de la BD
                nombre_tabla, esquema_final, nombre_clave
            )

            # Caso especial: buscar fecha en columna TIMESTAMP → comparar solo parte DATE
            if (tipo_columna in ('timestamp without time zone',
                                 'timestamp with time zone')
                    and self._es_fecha_sin_hora(valor)):
                sql = text(f'''
                    SELECT * FROM "{esquema_final}"."{nombre_tabla}"
                    WHERE CAST("{nombre_clave}" AS DATE) = :valor
                ''')
                valor_convertido = self._extraer_solo_fecha(valor)
            else:
                # Caso normal: WHERE "columna" = :valor
                sql = text(f'''
                    SELECT * FROM "{esquema_final}"."{nombre_tabla}"
                    WHERE "{nombre_clave}" = :valor
                ''')
                valor_convertido = self._convertir_valor(valor, tipo_columna)

            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(
                    sql, {"valor": valor_convertido}       # Parámetro seguro
                )
                columnas = result.keys()
                return [
                    {col: self._serializar_valor(row[i])
                     for i, col in enumerate(columnas)}
                    for row in result.fetchall()
                ]
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al filtrar "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

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
        if not datos:                                      # dict vacío o None
            raise ValueError("Los datos no pueden estar vacíos")

        esquema_final = (esquema or "public").strip()
        datos_finales = dict(datos)                        # Copia para no modificar el original

        columnas = ", ".join(f'"{k}"' for k in datos_finales.keys())
        # → '"codigo", "nombre", "stock", "valorunitario"'
        parametros = ", ".join(f":{k}" for k in datos_finales.keys())
        # → ':codigo, :nombre, :stock, :valorunitario'
        sql = text(
            f'INSERT INTO "{esquema_final}"."{nombre_tabla}" '
            f'({columnas}) VALUES ({parametros})'
        )
        # SQL final: INSERT INTO "public"."producto" ("codigo", ...) VALUES (:codigo, ...)

        try:
            valores = {}
            for key, val in datos_finales.items():
                if val is not None and isinstance(val, str):  # Solo convierte strings
                    tipo = await self._detectar_tipo_columna(
                        nombre_tabla, esquema_final, key
                    )
                    valores[key] = self._convertir_valor(val, tipo)  # "20" → int(20)
                else:
                    valores[key] = val                     # Ya es int/float: sin conversión

            engine = await self._obtener_engine()
            async with engine.begin() as conn:             # begin(): TRANSACCIÓN automática
                                                           # Commit si éxito, rollback si error
                result = await conn.execute(sql, valores)
                return result.rowcount > 0                 # True si insertó al menos 1 fila
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al insertar en "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

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

        esquema_final = (esquema or "public").strip()
        datos_finales = dict(datos)                        # Copia del diccionario

        clausula_set = ", ".join(
            f'"{k}" = :{k}' for k in datos_finales.keys()
        )
        # → '"nombre" = :nombre, "stock" = :stock'
        sql = text(f'''
            UPDATE "{esquema_final}"."{nombre_tabla}"
            SET {clausula_set}
            WHERE "{nombre_clave}" = :valor_clave
        ''')
        # :valor_clave es nombre fijo para no confundirse con los campos del SET.

        try:
            valores = {}
            for key, val in datos_finales.items():         # Conversión de tipos para SET
                if val is not None and isinstance(val, str):
                    tipo = await self._detectar_tipo_columna(
                        nombre_tabla, esquema_final, key
                    )
                    valores[key] = self._convertir_valor(val, tipo)
                else:
                    valores[key] = val

            tipo_clave = await self._detectar_tipo_columna(  # También convierte la PK
                nombre_tabla, esquema_final, nombre_clave
            )
            valores["valor_clave"] = self._convertir_valor(
                valor_clave, tipo_clave
            )

            engine = await self._obtener_engine()
            async with engine.begin() as conn:             # Transacción automática
                result = await conn.execute(sql, valores)
                return result.rowcount                     # Filas afectadas (0 o 1)
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al actualizar "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

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

        esquema_final = (esquema or "public").strip()

        sql = text(f'''
            DELETE FROM "{esquema_final}"."{nombre_tabla}"
            WHERE "{nombre_clave}" = :valor_clave
        ''')

        try:
            tipo_clave = await self._detectar_tipo_columna(  # Detecta tipo de la PK
                nombre_tabla, esquema_final, nombre_clave
            )
            valor_convertido = self._convertir_valor(        # Convierte al tipo correcto
                valor_clave, tipo_clave
            )

            engine = await self._obtener_engine()
            async with engine.begin() as conn:             # Transacción automática
                result = await conn.execute(
                    sql, {"valor_clave": valor_convertido}
                )
                return result.rowcount                     # Filas eliminadas (0 o 1)
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al eliminar de "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex
