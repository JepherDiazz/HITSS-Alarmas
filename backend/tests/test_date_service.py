from datetime import datetime

import pytest

from app.services.date_service import parse_alarm_datetime


def test_parse_pm_date():
    result = parse_alarm_datetime(
        "09-OCT-26 10.12.56.000000000 PM"
    )

    assert result == datetime(2026, 10, 9, 22, 12, 56)


def test_parse_am_date():
    result = parse_alarm_datetime(
        "10-OCT-26 03.13.48.000000000 AM"
    )

    assert result == datetime(2026, 10, 10, 3, 13, 48)


def test_parse_midnight():
    result = parse_alarm_datetime(
        "10-OCT-26 12.00.00.000000000 AM"
    )

    assert result.hour == 0


def test_parse_noon():
    result = parse_alarm_datetime(
        "10-OCT-26 12.00.00.000000000 PM"
    )

    assert result.hour == 12


def test_invalid_date():
    with pytest.raises(ValueError):
        parse_alarm_datetime("FECHA INCORRECTA")


def test_fractional_seconds():
    result = parse_alarm_datetime(
        "10-OCT-26 03.13.48.123456789 PM"
    )

    assert result.microsecond == 123456