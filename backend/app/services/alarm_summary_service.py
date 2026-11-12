from datetime import datetime

from app.services.alarm_processing_service import COLOMBIA_TZ

# Parte depProgramado sin ayuda
def summarize_today_alarms(
    alarm_records: list[dict],
    now: datetime | None = None
) -> dict:
    """Cuenta por hora las alarmas cuya fecha local es la de hoy."""
    current_time = now or datetime.now(COLOMBIA_TZ)

    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=COLOMBIA_TZ)
    else:
        current_time = current_time.astimezone(COLOMBIA_TZ)

    today = current_time.date()
    counts_by_hour = {}

    for alarm in alarm_records:
        created_at = alarm["FECHA_CREACION"]

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=COLOMBIA_TZ)
        else:
            created_at = created_at.astimezone(COLOMBIA_TZ)

        if created_at.date() == today:
            hour = created_at.hour
            counts_by_hour[hour] = counts_by_hour.get(hour, 0) + 1

    hours = [
        {"hour": f"{hour:02}:00", "total": counts_by_hour[hour]}
        for hour in sorted(counts_by_hour)
    ]

    return {
        "date": today.isoformat(),
        "total": sum(counts_by_hour.values()),
        "hours": hours
    }
