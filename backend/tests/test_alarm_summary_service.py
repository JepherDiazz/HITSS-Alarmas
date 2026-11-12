from datetime import datetime, timedelta

from app.api.alarms import alarm_records, get_today_summary, router
from app.services.alarm_processing_service import COLOMBIA_TZ
from app.services.alarm_summary_service import summarize_today_alarms


TODAY = datetime(2026, 11, 6, 12, 0, tzinfo=COLOMBIA_TZ)


def make_alarm(created_at):
    return {"FECHA_CREACION": created_at}


def test_summary_counts_today_alarms_by_hour_and_ignores_other_dates():
    alarms = [
        make_alarm(TODAY.replace(hour=8, minute=5)),
        make_alarm(TODAY.replace(hour=8, minute=30)),
        make_alarm(TODAY.replace(hour=8, minute=55)),
        make_alarm(TODAY.replace(hour=9, minute=10)),
        make_alarm(TODAY.replace(hour=9, minute=45)),
        make_alarm(TODAY - timedelta(days=1)),
        make_alarm(TODAY + timedelta(days=1)),
    ]

    result = summarize_today_alarms(alarms, TODAY)

    assert result == {
        "date": "2026-11-06",
        "total": 5,
        "hours": [
            {"hour": "08:00", "total": 3},
            {"hour": "09:00", "total": 2},
        ],
    }


def test_summary_is_empty_when_there_are_no_alarms_today():
    alarms = [
        make_alarm(TODAY - timedelta(days=1)),
        make_alarm(TODAY + timedelta(days=1)),
    ]

    result = summarize_today_alarms(alarms, TODAY)

    assert result == {"date": "2026-11-06", "total": 0, "hours": []}


def test_endpoint_returns_summary_for_imported_alarms():
    now = datetime.now(COLOMBIA_TZ)
    alarm_records.clear()
    alarm_records.extend([
        make_alarm(now.replace(hour=8, minute=10, second=0, microsecond=0)),
        make_alarm(now.replace(hour=8, minute=20, second=0, microsecond=0)),
        make_alarm(now - timedelta(days=1)),
    ])

    try:
        result = get_today_summary()
    finally:
        alarm_records.clear()

    assert any(
        route.path == "/summary/today"
        for route in router.routes
    )
    assert result == {
        "date": now.date().isoformat(),
        "total": 2,
        "hours": [{"hour": "08:00", "total": 2}],
    }
