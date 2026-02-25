"""Lee DB_PROVIDER y las cadenas de conexión desde .env."""

from config import Settings, get_settings


class ProveedorConexion:
    """Lee el proveedor activo y entrega la cadena de conexión."""

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()

    @property
    def proveedor_actual(self) -> str:
        """Proveedor activo según DB_PROVIDER en .env."""
        return self._settings.database.provider.lower().strip()

    def obtener_cadena_conexion(self) -> str:
        """Cadena de conexión del proveedor activo."""
        provider = self.proveedor_actual
        db_config = self._settings.database

        cadenas = {
            "postgres": db_config.postgres,
            "postgresql": db_config.postgres,
        }

        if provider not in cadenas:
            raise ValueError(
                f"Proveedor '{provider}' no soportado. "
                f"Opciones: {list(cadenas.keys())}"
            )

        cadena = cadenas[provider]
        if not cadena:
            raise ValueError(
                f"No se encontró cadena de conexión para '{provider}'. "
                f"Verificar DB_{provider.upper()} en .env"
            )

        return cadena
