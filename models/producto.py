"""Modelo Pydantic para la tabla producto."""

from pydantic import BaseModel        # BaseModel: clase base de Pydantic para validación.
                                       # Toda clase que hereda obtiene:
                                       # - Validación automática de tipos al crear instancia
                                       # - model_dump() para convertir a diccionario
                                       # - Documentación automática en Swagger UI


class Producto(BaseModel):
    """Representa un producto en la base de datos."""
    # Hereda de BaseModel → validación automática.
    # Los 4 campos corresponden a las 4 columnas de la tabla producto.

    codigo: str                        # Obligatorio. Corresponde a: VARCHAR(30) NOT NULL (PK)
    nombre: str                        # Obligatorio. Corresponde a: VARCHAR(100) NOT NULL

    stock: int | None = None           # Opcional. Corresponde a: INTEGER NOT NULL
    # int | None → acepta entero o None. = None → default si no se envía.
    # Si envían "abc", Pydantic rechaza con error 422.
    # Si envían "20" (string), Pydantic convierte a int(20) automáticamente.

    valorunitario: float | None = None # Opcional. Corresponde a: NUMERIC(14,2) NOT NULL
    # float | None → acepta decimal o None.
    # Usamos float (no Decimal) porque JSON no tiene tipo Decimal.
