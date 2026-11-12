import re
from datetime import datetime


MONTHS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12
}


def parse_alarm_datetime(date_string: str) -> datetime:
    """
    Convierte una fecha del CSV al formato datetime de Python.
    """

    pattern = (
        r"^(\d{2})-([A-Z]{3})-(\d{2}) "
        r"(\d{2})\.(\d{2})\.(\d{2})\.(\d{9}) ([AP]M)$"
    )

    match = re.fullmatch(pattern, date_string.strip())

    if not match:
        raise ValueError(f"Formato de fecha inválido: {date_string}")

    day, month, year, hour, minute, second, fraction, period = (
        match.groups()
    )

    month_number = MONTHS.get(month)

    if month_number is None:
        raise ValueError(f"Mes no reconocido: {month}")

    # Las fechas de nuestra muestra pertenecen al siglo XXI.
    year_number = 2000 + int(year)

    # Convertir formato de 12 horas a 24 horas.
    hour_number = int(hour)

    hour_number = hour_number % 12

    if period == "PM":
        hour_number += 12

    # datetime admite seis dígitos de microsegundos.
    microseconds = int(fraction[:6])

    return datetime(
        year=year_number,
        month=month_number,
        day=int(day),
        hour=hour_number,
        minute=int(minute),
        second=int(second),
        microsecond=microseconds
    )