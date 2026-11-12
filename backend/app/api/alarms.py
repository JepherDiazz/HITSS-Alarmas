from typing import Literal
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from app.services.alarm_csv_service import parse_alarm_csv
from app.services.alarm_processing_service import (
    normalize_alarm_record,
    classify_alarm
)
from io import BytesIO
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from app.services.alarm_processing_service import COLOMBIA_TZ
from app.services.alarm_summary_service import summarize_today_alarms


router = APIRouter()

# Almacenamiento temporal en memoria.
alarm_records = []


@router.post("/import")
async def import_alarms(file: UploadFile = File(...)):
    """
    Recibe un CSV, valida y normaliza sus registros.
    """

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener extensión CSV."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío."
        )

    try:
        raw_records = parse_alarm_csv(content)

        normalized_records = [
            normalize_alarm_record(record)
            for record in raw_records
        ]

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    # Reemplazar los registros de la importación anterior.
    alarm_records.clear()
    alarm_records.extend(normalized_records)

    return {
        "message": "Archivo importado correctamente.",
        "filename": file.filename,
        "total": len(alarm_records)
    }


@router.get("/export")
def export_alarms(
    level: Literal["NORMAL", "WARN", "CRITICO"] | None = Query(
        default=None
    )
):
    """
    Exporta las alarmas visibles según el filtro seleccionado.
    """

    if not alarm_records:
        raise HTTPException(
            status_code=400,
            detail="Primero debes importar un archivo CSV."
        )

    # Obtener las alarmas clasificadas.
    classified_records = [
        classify_alarm(record)
        for record in alarm_records
    ]

    # Aplicar el filtro solicitado.
    if level is not None:
        classified_records = [
            record for record in classified_records
            if record["NIVEL_ALERTA"] == level
        ]

    # Crear libro y hoja Excel.
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Alarmas"

    headers = [
        "ID Alarma",
        "2G",
        "3G",
        "4G",
        "Fecha creación",
        "Municipio",
        "Departamento",
        "Notificada",
        "Tecnologías disponibles",
        "Duración",
        "Criticidad"
    ]

    worksheet.append(headers)

    # Agregar los registros.
    for alarm in classified_records:

        created_at = alarm["FECHA_CREACION"]

        if created_at.tzinfo is not None:
            created_at = created_at.astimezone(
                COLOMBIA_TZ
            ).replace(tzinfo=None)

        worksheet.append([
            alarm["ID_ALARMA"],
            alarm["2G"],
            alarm["3G"],
            alarm["4G"],
            created_at,
            alarm["MUNICIPIO"],
            alarm["DEPARTAMENTO"],
            alarm["NOTIFICADA"],
            ", ".join(alarm["TECNOLOGIAS_DISPONIBLES"]),
            alarm["DURACION"],
            alarm["NIVEL_ALERTA"]
        ])

    # Dar formato a los encabezados.
    for cell in worksheet[1]:
        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="1F4E78"
        )
        cell.alignment = Alignment(
            horizontal="center"
        )

    # Configurar la hoja.
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    # Formato de fecha.
    for cell in worksheet["E"][1:]:
        cell.number_format = "dd/mm/yyyy hh:mm:ss"

    # Ajustar ancho de columnas.
    for column_cells in worksheet.columns:
        column_number = column_cells[0].column
        column_letter = get_column_letter(column_number)

        max_length = max(
            len(str(cell.value or ""))
            for cell in column_cells
        )

        worksheet.column_dimensions[column_letter].width = (
            min(max_length + 3, 35)
        )

    # Preparar archivo en memoria.
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="alarmas.xlsx"'
            )
        }
    )

#Parte de programacion sin ayuda
@router.get("/summary/today")
def get_today_summary():
    """Resume por hora las alarmas creadas hoy en Colombia."""
    return summarize_today_alarms(alarm_records)


@router.get("/")
def get_alarms(
    level: Literal["NORMAL", "WARN", "CRITICO"] | None = Query(
        default=None
    )
):
    """
    Consulta las alarmas y permite filtrar por nivel.
    """

    # Recalcular la clasificación para mantener
    # actualizada la duración de las alarmas.
    classified_records = [
        classify_alarm(record)
        for record in alarm_records
    ]

    if level is not None:
        classified_records = [
            record
            for record in classified_records
            if record["NIVEL_ALERTA"] == level
        ]

    return {
        "total": len(classified_records),
        "items": classified_records
    }
