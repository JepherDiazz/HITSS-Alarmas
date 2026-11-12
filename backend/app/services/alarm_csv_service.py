import csv
import io


EXPECTED_COLUMNS = [
    "ID_ALARMA",
    "2G",
    "3G",
    "4G",
    "FECHA_CREACION",
    "MUNICIPIO",
    "DEPARTAMENTO",
    "NOTIFICADA"
]


def parse_alarm_csv(file_content: bytes) -> list[dict[str, str]]:
    """
    Convierte el contenido de un archivo CSV en una lista de registros.

    El archivo debe utilizar el separador | y contener
    las ocho columnas esperadas.
    """

    # 1. Decodificar el contenido del archivo.
    try:
        content = file_content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(
            "El archivo debe utilizar codificación UTF-8."
        ) from error

    # 2. Crear el lector CSV con separador pipe.
    reader = csv.DictReader(
        io.StringIO(content),
        delimiter="|"
    )

    # 3. Comprobar que existan encabezados.
    if reader.fieldnames is None:
        raise ValueError("El archivo está vacío o no tiene encabezados.")

    columns = [
        (column or "").strip()
        for column in reader.fieldnames
    ]

    # 4. Comprobar que las columnas sean las esperadas.
    if columns != EXPECTED_COLUMNS:
        raise ValueError(
            f"Las columnas del archivo no coinciden. "
            f"Columnas esperadas: {EXPECTED_COLUMNS}. "
            f"Columnas recibidas: {columns}."
        )

    records = []

    # 5. Recorrer y validar los registros.
    for row in reader:

        # Detectar registros con columnas adicionales.
        if None in row:
            raise ValueError(
                f"El registro de la línea {reader.line_num} "
                "contiene columnas adicionales."
            )

        # Limpiar espacios en los valores.
        cleaned_row = {
            key: (value or "").strip()
            for key, value in row.items()
        }

        # Detectar campos vacíos.
        empty_fields = [
            field
            for field, value in cleaned_row.items()
            if not value
        ]

        if empty_fields:
            raise ValueError(
                f"Registro de la línea {reader.line_num} "
                f"con campos vacíos: {empty_fields}."
            )

        records.append(cleaned_row)

    # 6. Comprobar que existan registros.
    if not records:
        raise ValueError("El archivo no contiene registros.")

    return records