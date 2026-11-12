
# Documentación técnica — HITSS Alarmas

## 1. Descripción del proyecto

HITSS Alarmas es una aplicación Full Stack desarrollada para la prueba técnica de Desarrollador Python Jr de HITSS Colombia.

Su objetivo es importar, procesar, clasificar y visualizar alarmas operativas, aplicando reglas de negocio relacionadas con la disponibilidad tecnológica, capacidad y tiempo de actividad.

## 2. Arquitectura de la solución

La aplicación utiliza una arquitectura desacoplada compuesta por dos componentes principales:

### Backend
Desarrollado con Python y FastAPI.

Responsabilidades:
- Recepción e importación de archivos CSV.
- Validación y normalización de registros.
- Conversión de fechas.
- Clasificación de alarmas.
- Cálculo de duración acumulada.
- Generación de archivos Excel.
- Servicio de resumen diario.

### Frontend
Desarrollado con React y Vite.

Responsabilidades:
- Interfaz de usuario.
- Importación de archivos CSV.
- Visualización de indicadores.
- Tabla de alarmas.
- Filtros de criticidad.
- Exportación de información.
- Visualización del resumen diario.

### Comunicación

El frontend y backend se comunican mediante servicios REST utilizando HTTP y JSON.

## 3. Reglas de negocio

Una alarma cumple las condiciones base cuando:

1. Tiene al menos una tecnología disponible, considerando disponibles los valores mayores o iguales a cero.
2. Al menos una de las tecnologías disponibles tiene un valor exactamente igual a 100.
3. El campo NOTIFICADA tiene el valor N.

La interpretación de capacidad adoptada considera suficiente que una tecnología disponible tenga un valor de 100.

### Clasificación

- NORMAL: no cumple las condiciones base o tiene una duración de hasta una hora.
- WARN: duración superior a una hora y menor o igual a 24 horas.
- CRÍTICO: duración superior a 24 horas.

## 4. Procesamiento de datos

El archivo de entrada utiliza el separador vertical `|`.

El procesamiento contempla:
- Validación de encabezados.
- Validación de campos obligatorios.
- Conversión de identificadores y tecnologías a enteros.
- Interpretación del formato de fecha original.
- Manejo de zona horaria de Bogotá.
- Cálculo de duración acumulada.

El sistema trabaja con los siguientes campos originales:

ID_ALARMA, 2G, 3G, 4G, FECHA_CREACION, MUNICIPIO, DEPARTAMENTO y NOTIFICADA.

## 5. Servicios API REST

| Método | Endpoint | Responsabilidad |
|---|---|---|
| GET | / | Información inicial |
| GET | /health | Estado del backend |
| POST | /api/alarms/import | Importar CSV |
| GET | /api/alarms/ | Consultar alarmas |
| GET | /api/alarms/export | Exportar Excel |
| GET | /api/alarms/summary/today | Resumen diario |

## 6. Resumen diario

El servicio `alarm_summary_service.py` calcula las alarmas creadas durante el día actual según la zona horaria de Bogotá.

Su resultado contiene:
- Fecha consultada.
- Total de alarmas del día.
- Conteo de alarmas agrupadas por hora.

El servicio permite utilizar una fecha controlada mediante un parámetro opcional `now`, facilitando las pruebas con fechas específicas.

### Desarrollo individual

El servicio `alarm_summary_service.py` fue desarrollado íntegramente por el candidato, sin asistencia de IA, en cumplimiento de la condición obligatoria de la prueba técnica.

## 7. Exportación Excel

La aplicación genera archivos XLSX mediante OpenPyXL.

La exportación respeta el filtro de criticidad seleccionado y contiene:
- Los ocho campos originales.
- Tecnologías disponibles.
- Duración acumulada.
- Nivel de criticidad.

El archivo incluye encabezados, filtros y formato de presentación.

## 8. Pruebas y validación

En la última ejecución del backend se obtuvieron:

- 17 pruebas recopiladas.
- 17 pruebas superadas.
- 0 pruebas fallidas.

Las pruebas contemplan:
- Conversión de fechas.
- Manejo de AM y PM.
- Límites de una y 24 horas.
- Condiciones de disponibilidad tecnológica.
- Estado de notificación.
- Fechas futuras.
- Agrupación horaria del resumen diario.

El frontend también completó satisfactoriamente la compilación de producción mediante Vite.

## 9. Consideraciones técnicas

- Los registros importados se mantienen temporalmente en memoria.
- Al reiniciar el backend se requiere una nueva importación.
- La aplicación utiliza la zona horaria de Bogotá para el tratamiento de fechas.
- La API permite consultar las alarmas por nivel de criticidad.
- El frontend y backend se ejecutan de forma independiente.

## 10. Tecnologías utilizadas

- Python 3.13
- FastAPI
- Uvicorn
- OpenPyXL
- Pytest
- HTTPX
- JavaScript
- React
- Vite
- CSS
- Visual Studio Code

## 11. Objetivo de la solución

Demostrar la capacidad para desarrollar una aplicación Full Stack, implementar reglas de negocio, crear y consumir servicios REST, procesar información y aplicar pruebas para verificar el funcionamiento de los componentes.
