from datetime import datetime, timedelta

import pytest

from app.services.alarm_processing_service import (
    classify_alarm,
    COLOMBIA_TZ
)


NOW = datetime(2026, 11, 6, 12, 0, tzinfo=COLOMBIA_TZ)


def create_alarm(hours_ago, seconds_ago=0, **overrides):
    record = {
        "ID_ALARMA": 12345,
        "2G": 100,
        "3G": 60,
        "4G": -100,
        "FECHA_CREACION": (
            NOW.replace(tzinfo=None)
            - timedelta(hours=hours_ago, seconds=seconds_ago)
        ),
        "MUNICIPIO": "Bogotá",
        "DEPARTAMENTO": "Cundinamarca",
        "NOTIFICADA": "N"
    }

    record.update(overrides)
    return record


def test_one_available_technology_at_100():
    alarm = classify_alarm(create_alarm(25), NOW)

    assert alarm["CUMPLE_CONDICIONES_BASE"] is True
    assert alarm["NIVEL_ALERTA"] == "CRITICO"


def test_exactly_one_hour_is_normal():
    alarm = classify_alarm(create_alarm(1), NOW)

    assert alarm["NIVEL_ALERTA"] == "NORMAL"


def test_more_than_one_hour_is_warn():
    alarm = classify_alarm(create_alarm(1, 1), NOW)

    assert alarm["NIVEL_ALERTA"] == "WARN"


def test_exactly_24_hours_is_warn():
    alarm = classify_alarm(create_alarm(24), NOW)

    assert alarm["NIVEL_ALERTA"] == "WARN"


def test_more_than_24_hours_is_critical():
    alarm = classify_alarm(create_alarm(24, 1), NOW)

    assert alarm["NIVEL_ALERTA"] == "CRITICO"


def test_notified_alarm_is_normal():
    alarm = classify_alarm(
        create_alarm(25, NOTIFICADA="S"),
        NOW
    )

    assert alarm["CUMPLE_CONDICIONES_BASE"] is False
    assert alarm["NIVEL_ALERTA"] == "NORMAL"


def test_no_available_technologies():
    alarm = classify_alarm(
        create_alarm(25, **{"2G": -100, "3G": -100, "4G": -100}),
        NOW
    )

    assert alarm["CUMPLE_CONDICIONES_BASE"] is False
    assert alarm["NIVEL_ALERTA"] == "NORMAL"


def test_future_alarm_date_is_rejected():
    alarm = create_alarm(-1)

    with pytest.raises(ValueError):
        classify_alarm(alarm, NOW)