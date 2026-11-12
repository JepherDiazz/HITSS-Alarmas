
# HITSS Alarmas — Sistema de monitoreo y clasificación

Aplicación Full Stack desarrollada como solución a la prueba técnica para el cargo de Desarrollador Python Jr en HITSS Colombia.

El sistema permite importar archivos CSV de alarmas, procesar la información, clasificar los registros según su criticidad, visualizar los resultados en un dashboard y exportar la información a Excel.

## 1. Tecnologías utilizadas

### Backend
- Python 3.13
- FastAPI
- Uvicorn
- OpenPyXL
- Pytest

### Frontend
- React
- JavaScript
- Vite
- CSS

### Herramientas
- Visual Studio Code
- Git
- Swagger UI
- Rainbow CSV

## 2. Arquitectura

El proyecto utiliza una arquitectura desacoplada:

- Frontend: aplicación desarrollada con React y Vite.
- Backend: servicios desarrollados con Python y FastAPI.
- Comunicación: API REST mediante HTTP y respuestas JSON.

El frontend consume los servicios del backend de manera independiente.

## 3. Estructura del proyecto

```text
HITSS-Alarmas/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── alarms.py
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── alarm_csv_service.py
│   │   │   ├── alarm_processing_service.py
│   │   │   ├── alarm_summary_service.py
│   │   │   └── date_service.py
│   │   └── main.py
│   │
│   ├── data/
│   │   └── input/
│   │       └── alarmas.csv
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   └── package.json
│
├── .gitignore
└── README.md
```

## 4. Funcionalidades implementadas

### Importación de alarmas
- Importación de archivos CSV desde la interfaz web.
- Separador de campos: `|`.
- Validación de las ocho columnas requeridas.
- Normalización de los registros y validación de datos.

### Clasificación por criticidad

Una alarma debe cumplir las siguientes condiciones base:

1. Las tecnologías disponibles (2G, 3G y 4G) tienen valores mayores o iguales a cero.
2. Al menos una tecnología disponible tiene un valor exactamente igual a 100.
3. El campo NOTIFICADA tiene el valor N.

Clasificación:

- NORMAL: no cumple todas las condiciones base o su duración es de hasta una hora.
- WARN: duración superior a una hora y menor o igual a 24 horas.
- CRÍTICO: duración superior a 24 horas.

### Dashboard
- Visualización de alarmas en una tabla.
- Duración acumulada desde la creación hasta el momento actual.
- Indicadores de criticidad.
- Filtros por NORMAL, WARN y CRÍTICO.
- Vista de todos los registros.
- Paginación.

### Exportación Excel
- Generación de archivos XLSX.
- Exportación de todos los registros o de la categoría seleccionada.
- Encabezados, filtros y formato de columnas.

### Resumen diario
- Consulta de alarmas creadas durante el día actual en la zona horaria de Bogotá.
- Agrupación por hora.
- Conteo total de alarmas.
- Visualización mediante un panel en React.

## 5. Servicios API REST

| Método | Endpoint | Descripción |
|---|---|---|
| GET | / | Inicio de la API |
| GET | /health | Estado del backend |
| POST | /api/alarms/import | Importación de CSV |
| GET | /api/alarms/ | Consulta y filtros |
| GET | /api/alarms/export | Exportación Excel |
| GET | /api/alarms/summary/today | Resumen diario |

Documentación interactiva disponible en:

`http://127.0.0.1:8000/docs`

## 6. Instalación y ejecución

### Requisitos previos
- Python 3.13 o compatible.
- Node.js compatible con Vite.
- npm.

### Backend

Desde la carpeta principal del proyecto:

```powershell
python -m venv .venv
```

Instalar las dependencias:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
```

Entrar al backend:

```powershell
cd backend
```

Iniciar FastAPI:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

El backend estará disponible en:

`http://127.0.0.1:8000`

### Frontend

Abrir otra terminal desde la carpeta principal:

```powershell
cd frontend
```

Instalar dependencias:

```powershell
npm install
```

Ejecutar React:

```powershell
npm run dev
```

El frontend estará disponible en:

`http://localhost:5173`

## 7. Pruebas automatizadas

Desde la carpeta backend ejecutar:

```powershell
..\.venv\Scripts\python.exe -m pytest tests -v
```

Resultado de la última ejecución:

- 17 pruebas recopiladas.
- 17 pruebas superadas.
- 0 pruebas fallidas.

## 8. Consideraciones técnicas

- Los registros importados se almacenan temporalmente en memoria.
- Al reiniciar el backend es necesario importar nuevamente el CSV.
- La interpretación de las fechas utiliza la zona horaria de Colombia.
- El resumen diario agrupa las alarmas utilizando la fecha local de Bogotá.
- El criterio de capacidad al límite considera que al menos una tecnología disponible debe tener un valor de 100.

## 9. Desarrollo individual y uso de IA

Se utilizaron asistentes de inteligencia artificial como apoyo en el desarrollo de los componentes permitidos por la prueba.

El servicio `alarm_summary_service.py` fue desarrollado íntegramente por el candidato, sin asistencia de IA, de acuerdo con la condición establecida por HITSS.

## 10. Autor

Proyecto desarrollado como parte del proceso de selección para el cargo de Desarrollador Python Jr — HITSS Colombia.
