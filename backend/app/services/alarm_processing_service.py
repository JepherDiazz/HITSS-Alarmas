from datetime import datetime, timedelta, timezone

from app.services.date_service import parse_alarm_datetime

COLOMBIA_TZ = timezone(
    timedelta(hours=-5),
    name="America/Bogota"
)


TECHNOLOGY_FIELDS = ["2G", "3G", "4G"]


def normalize_alarm_record(record: dict) -> dict:
    """
    Convierte un registro del CSV en un registro normalizado.

    Convierte:
    - ID_ALARMA a entero.
    - 2G, 3G y 4G a enteros.
    - FECHA_CREACION a datetime.
    """

    try:
        alarm_id = int(record["ID_ALARMA"])

        technologies = {
            field: int(record[field])
            for field in TECHNOLOGY_FIELDS
        }

        created_at = parse_alarm_datetime(
            record["FECHA_CREACION"]
        )

        created_at = created_at.replace(
            tzinfo=COLOMBIA_TZ
    )

    except KeyError as error:
        raise ValueError(
            f"Falta el campo obligatorio: {error}"
        ) from error

    except ValueError as error:
        raise ValueError(
            f"Registro de alarma inválido: {error}"
        ) from error

    notification = record["NOTIFICADA"].strip().upper()

    if notification not in ("N", "S"):
        raise ValueError(
            f"Estado de notificación inválido: {notification}"
        )

    return {
        "ID_ALARMA": alarm_id,
        "2G": technologies["2G"],
        "3G": technologies["3G"],
        "4G": technologies["4G"],
        "FECHA_CREACION": created_at,
        "MUNICIPIO": record["MUNICIPIO"].strip(),
        "DEPARTAMENTO": record["DEPARTAMENTO"].strip(),
        "NOTIFICADA": notification
    }


def classify_alarm(
    record: dict,
    now: datetime | None = None
) -> dict:
    """
    Clasifica una alarma según disponibilidad tecnológica,
    capacidad y estado de notificación.
    """

    technologies = {
        "2G": record["2G"],
        "3G": record["3G"],
        "4G": record["4G"]
    }

    # Identificar las tecnologías disponibles.
    available_technologies = {
        technology: value
        for technology, value in technologies.items()
        if value >= 0
    }

    # Comprobar si alguna tecnología disponible está al 100%.
    has_capacity_at_limit = any(
        value == 100
        for value in available_technologies.values()
    )

    # Comprobar el estado de notificación.
    is_not_notified = record["NOTIFICADA"] == "N"

    # Evaluar todas las condiciones base.
    meets_base_conditions = (
        bool(available_technologies)
        and has_capacity_at_limit
        and is_not_notified
    )

    # Interpretar la fecha como hora de Colombia.
    created_at = record["FECHA_CREACION"]

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=COLOMBIA_TZ)
    else:
        created_at = created_at.astimezone(COLOMBIA_TZ)

    current_time = now or datetime.now(COLOMBIA_TZ)

    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=COLOMBIA_TZ)
    else:
        current_time = current_time.astimezone(COLOMBIA_TZ)

    # Calcular duración acumulada.
    elapsed_time = current_time - created_at

    if elapsed_time.total_seconds() < 0:
        raise ValueError(
            "La fecha de creación no puede estar en el futuro."
        )

    duration_seconds = int(elapsed_time.total_seconds())

    # Clasificar según las condiciones base y antigüedad.
    if not meets_base_conditions:
        alert_level = "NORMAL"

    elif elapsed_time > timedelta(hours=24):
        alert_level = "CRITICO"

    elif elapsed_time > timedelta(hours=1):
        alert_level = "WARN"

    else:
        alert_level = "NORMAL"

    # Formatear duración: días, horas, minutos y segundos.
    days, remainder = divmod(duration_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted_duration = (
        f"{days}d {hours:02}:{minutes:02}:{seconds:02}"
    )

    return {
        **record,
        "TECNOLOGIAS_DISPONIBLES": list(
            available_technologies.keys()
        ),
        "CUMPLE_CONDICIONES_BASE": meets_base_conditions,
        "DURACION_SEGUNDOS": duration_seconds,
        "DURACION": formatted_duration,
        "NIVEL_ALERTA": alert_level
    }