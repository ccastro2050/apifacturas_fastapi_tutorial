"""Lee DB_PROVIDER y las cadenas de conexión desde .env."""
# Implementación concreta del contrato IProveedorConexion.
# Lee la configuración centralizada (config.py) y expone el proveedor activo
# y su cadena de conexión.

from config import Settings, get_settings  # Settings: clase con toda la configuración.
                                            # get_settings: singleton que retorna Settings cacheado.


class ProveedorConexion:
    """Lee el proveedor activo y entrega la cadena de conexión."""
    # NO hereda de IProveedorConexion, pero CUMPLE el contrato
    # porque tiene los mismos miembros (duck typing / Protocol).

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
    # settings: parámetro opcional. Si no se pasa, usa get_settings() (singleton).
    # "or": si settings es None (falsy), usa get_settings().
    # self._settings: guarda la referencia como atributo privado (_prefijo).

    @property
    def proveedor_actual(self) -> str:
        """Proveedor activo según DB_PROVIDER en .env."""
        return self._settings.database.provider.lower().strip()
    # self._settings.database → objeto DatabaseSettings.
    # .provider → lee DB_PROVIDER del .env (ej: "postgres").
    # .lower() → minúsculas: "POSTGRES" → "postgres".
    # .strip() → elimina espacios: " postgres " → "postgres".

    def obtener_cadena_conexion(self) -> str:
        """Cadena de conexión del proveedor activo."""
        provider = self.proveedor_actual       # Nombre normalizado (ej: "postgres")
        db_config = self._settings.database    # Atajo para no repetir self._settings.database

        cadenas = {
            "postgres": db_config.postgres,    # Lee DB_POSTGRES del .env
            "postgresql": db_config.postgres,  # Alias: apunta a la misma cadena
        }
        # Diccionario: nombre de proveedor → cadena de conexión.
        # En el proyecto completo también incluye sqlserver, mysql, mariadb.

        if provider not in cadenas:            # Validación: proveedor no soportado
            raise ValueError(
                f"Proveedor '{provider}' no soportado. "
                f"Opciones: {list(cadenas.keys())}"
            )

        cadena = cadenas[provider]             # Obtiene la cadena correspondiente
        if not cadena:                         # Validación: cadena vacía (no configurada)
            raise ValueError(
                f"No se encontró cadena de conexión para '{provider}'. "
                f"Verificar DB_{provider.upper()} en .env"
            )

        return cadena                          # Ej: "postgresql+asyncpg://postgres:postgres@localhost:5432/..."
