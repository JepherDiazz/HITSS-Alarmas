import { useEffect, useMemo, useRef, useState } from "react";
import {
    checkApiHealth,
    getAlarms,
    importAlarms,
    exportAlarms,
    getTodaySummary
} from "./services/api";
import "./App.css";

const PAGE_SIZE = 20;

const FILTERS = [
    { value: "ALL", label: "Todos" },
    { value: "NORMAL", label: "Normal" },
    { value: "WARN", label: "Warn" },
    { value: "CRITICO", label: "Crítico" }
];

function formatDate(value) {
    if (!value) return "-";

    return new Date(value).toLocaleString("es-CO", {
        dateStyle: "short",
        timeStyle: "short",
        timeZone: "America/Bogota"
    });
}

function App() {
    const [summary, setSummary] = useState(null);
    const [summaryOpen, setSummaryOpen] = useState(false);
    const [loadingSummary, setLoadingSummary] = useState(false);
    const [exporting, setExporting] = useState(false);
    const [alarms, setAlarms] = useState([]);
    const [filter, setFilter] = useState("ALL");
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [connected, setConnected] = useState(false);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    const fileInputRef = useRef(null);

    // Consultar el backend cuando se inicia la aplicación.
    useEffect(() => {
        async function initializeDashboard() {
            try {
                await checkApiHealth();
                setConnected(true);

                const result = await getAlarms();
                setAlarms(result.items || []);
            } catch (err) {
                setConnected(false);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }

        initializeDashboard();
    }, []);

    // Filtrar las alarmas según su nivel de criticidad.
    const filteredAlarms = useMemo(() => {
        if (filter === "ALL") return alarms;

        return alarms.filter(
            (alarm) => alarm.NIVEL_ALERTA === filter
        );
    }, [alarms, filter]);

    // Calcular los indicadores del dashboard.
    const statistics = useMemo(() => ({
        total: alarms.length,
        normal: alarms.filter(
            (alarm) => alarm.NIVEL_ALERTA === "NORMAL"
        ).length,
        warn: alarms.filter(
            (alarm) => alarm.NIVEL_ALERTA === "WARN"
        ).length,
        critical: alarms.filter(
            (alarm) => alarm.NIVEL_ALERTA === "CRITICO"
        ).length
    }), [alarms]);

    // Preparar la paginación.
    const totalPages = Math.max(
        1,
        Math.ceil(filteredAlarms.length / PAGE_SIZE)
    );

    const currentPage = Math.min(page, totalPages);

    const visibleAlarms = filteredAlarms.slice(
        (currentPage - 1) * PAGE_SIZE,
        currentPage * PAGE_SIZE
    );

    // Importar un archivo CSV.
    async function handleFileChange(event) {
        const file = event.target.files?.[0];

        if (!file) return;

        setError("");
        setMessage("");

        if (!file.name.toLowerCase().endsWith(".csv")) {
            setError("Selecciona un archivo con extensión CSV.");
            event.target.value = "";
            return;
        }

        setUploading(true);

        try {
            const imported = await importAlarms(file);
            const result = await getAlarms();

            setAlarms(result.items || []);
            setFilter("ALL");
            setPage(1);

            setMessage(
                `${imported.message} Registros importados: ${imported.total}.`
            );
        } catch (err) {
            setError(err.message);
        } finally {
            setUploading(false);
            event.target.value = "";
        }
    }


    async function handleExport() {
    setError("");
    setMessage("");
    setExporting(true);

    try {
        const level = filter === "ALL" ? "" : filter;

        const filename = await exportAlarms(level);

        setMessage(
            `Archivo ${filename} descargado correctamente. ` +
            `Registros exportados: ${filteredAlarms.length}.`
        );

    } catch (err) {
        setError(err.message);
    } finally {
        setExporting(false);
    }
  }


  async function handleSummary() {
    setError("");
    setMessage("");
    setLoadingSummary(true);

    try {
        const data = await getTodaySummary();

        setSummary(data);
        setSummaryOpen(true);

    } catch (err) {
        setError(err.message);
    } finally {
        setLoadingSummary(false);
    }
  }

    function changeFilter(value) {
        setFilter(value);
        setPage(1);
    }

    return (
        <div className="app-container">

            <header className="topbar">
                <div className="brand">
                    <div className="brand-icon">H</div>

                    <div>
                        <h1>HITSS Alarmas</h1>
                        <p>Panel de monitoreo y criticidad</p>
                    </div>
                </div>

                <div className="connection-status">
                    <span className={connected ? "status-dot online" : "status-dot offline"} />
                    {connected ? "Backend conectado" : "Backend desconectado"}
                </div>
            </header>

            <main className="dashboard">

                <section className="welcome-section">
                    <div>
                        <p className="eyebrow">CENTRO DE OPERACIONES</p>
                        <h2>Monitoreo de alarmas</h2>
                        <p>
                            Consulta, importa y clasifica las alarmas
                            según su antigüedad y criticidad.
                        </p>
                    </div>

                    <div className="upload-container">
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".csv,text/csv"
                            onChange={handleFileChange}
                            hidden
                        />

                        <button
                            className="upload-button"
                            onClick={() => fileInputRef.current?.click()}
                            disabled={uploading || !connected}
                        >
                            {uploading ? "Importando..." : "↑ Importar CSV"}
                        </button>

                        <button
                            className="summary-button"
                            onClick={handleSummary}
                            disabled={loadingSummary || !connected}
                        >
                            {loadingSummary ? "Consultando..." : "▤ Resumen del día"}
                        </button>
                    </div>
                </section>

                {error && (
                    <div className="alert-message error-message">
                        {error}
                    </div>
                )}

                {message && (
                    <div className="alert-message success-message">
                        {message}
                    </div>
                )}

                {summaryOpen && summary && (
    <div
        className="modal-backdrop"
        onClick={(event) => {
            if (event.target === event.currentTarget) {
                setSummaryOpen(false);
            }
        }}
    >
        <section
            className="summary-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="summary-title"
        >
            <div className="summary-modal-header">
                <div>
                    <p className="eyebrow">REPORTE OPERATIVO</p>
                    <h3 id="summary-title">Resumen del día</h3>
                    <p>Fecha consultada: {summary.date}</p>
                </div>

                <button
                    className="modal-close"
                    onClick={() => setSummaryOpen(false)}
                    aria-label="Cerrar resumen"
                >
                    ×
                </button>
            </div>

            <div className="summary-total-card">
                <span>Total de alarmas creadas hoy</span>
                <strong>
                    {summary.total.toLocaleString("es-CO")}
                </strong>
            </div>

            <div className="summary-hours-section">
                <h4>Alarmas creadas por hora</h4>

                {summary.hours.length === 0 ? (
                    <div className="summary-empty">
                        <span className="summary-empty-icon">◷</span>
                        <strong>No hay alarmas registradas hoy</strong>
                        <p>
                            No se encontraron alarmas creadas
                            durante esta fecha.
                        </p>
                    </div>
                ) : (
                    <div className="summary-hours-list">
                        {summary.hours.map((item) => {
                            const maxTotal = Math.max(
                                ...summary.hours.map(
                                    (hour) => hour.total
                                ),
                                1
                            );

                            const percentage =
                                (item.total / maxTotal) * 100;

                            return (
                                <div
                                    className="summary-hour-row"
                                    key={item.hour}
                                >
                                    <span className="hour-label">
                                        {item.hour}
                                    </span>

                                    <div className="hour-bar-background">
                                        <div
                                            className="hour-bar-fill"
                                            style={{
                                                width: `${percentage}%`
                                            }}
                                        />
                                    </div>

                                    <strong>{item.total}</strong>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            <div className="summary-modal-footer">
                <button
                    onClick={() => setSummaryOpen(false)}
                >
                    Cerrar
                </button>
            </div>
        </section>
    </div>
)}

                <section className="statistics-grid">

                    <div className="stat-card total-card">
                        <span className="stat-label">Total de alarmas</span>
                        <strong>{statistics.total.toLocaleString("es-CO")}</strong>
                        <span className="stat-description">
                            Registros cargados
                        </span>
                    </div>

                    <div className="stat-card normal-card">
                        <span className="stat-label">Normales</span>
                        <strong>{statistics.normal.toLocaleString("es-CO")}</strong>
                        <span className="stat-description">
                            Sin alerta especial
                        </span>
                    </div>

                    <div className="stat-card warn-card">
                        <span className="stat-label">Warn</span>
                        <strong>{statistics.warn.toLocaleString("es-CO")}</strong>
                        <span className="stat-description">
                            Entre 1 y 24 horas
                        </span>
                    </div>

                    <div className="stat-card critical-card">
                        <span className="stat-label">Críticas</span>
                        <strong>{statistics.critical.toLocaleString("es-CO")}</strong>
                        <span className="stat-description">
                            Más de 24 horas
                        </span>
                    </div>

                </section>

                <section className="table-section">

                    <div className="table-header">
                        <div>
                            <h3>Registro de alarmas</h3>
                            <p>
                                {filteredAlarms.length.toLocaleString("es-CO")}
                                {" "}registros encontrados
                            </p>
                        </div>

                        <div className="filter-buttons">
                            {FILTERS.map((item) => (
                                <button
                                    key={item.value}
                                    className={
                                        filter === item.value
                                            ? "filter-button active"
                                            : "filter-button"
                                    }
                                    onClick={() => changeFilter(item.value)}
                                >
                                    {item.label}
                                </button>
                            ))}<button
                              className="export-button"
                                onClick={handleExport}
                                    disabled={exporting || !connected}
                                >
                                      {exporting ? "Exportando..." : "↓ Exportar Excel"}
                                </button>
                        </div>
                    </div>

                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID Alarma</th>
                                    <th>2G</th>
                                    <th>3G</th>
                                    <th>4G</th>
                                    <th>Fecha creación</th>
                                    <th>Municipio</th>
                                    <th>Departamento</th>
                                    <th>Notificada</th>
                                    <th>Tecnologías disponibles</th>
                                    <th>Duración</th>
                                    <th>Criticidad</th>
                                </tr>
                            </thead>

                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan="11" className="empty-state">
                                            Cargando información...
                                        </td>
                                    </tr>
                                ) : visibleAlarms.length === 0 ? (
                                    <tr>
                                        <td colSpan="11" className="empty-state">
                                            No hay alarmas para mostrar.
                                            Importa un archivo CSV para comenzar.
                                        </td>
                                    </tr>
                                ) : (
                                    visibleAlarms.map((alarm) => (
                                        <tr key={alarm.ID_ALARMA}>
                                            <td className="alarm-id">
                                                {alarm.ID_ALARMA}
                                            </td>
                                            <td>{alarm["2G"]}</td>
                                            <td>{alarm["3G"]}</td>
                                            <td>{alarm["4G"]}</td>
                                            <td>{formatDate(alarm.FECHA_CREACION)}</td>
                                            <td>{alarm.MUNICIPIO}</td>
                                            <td>{alarm.DEPARTAMENTO}</td>
                                            <td>{alarm.NOTIFICADA}</td>
                                            <td>
                                                {alarm.TECNOLOGIAS_DISPONIBLES.join(", ")}
                                            </td>
                                            <td className="duration-cell">
                                                {alarm.DURACION}
                                            </td>
                                            <td>
                                                <span
                                                    className={`severity-badge ${alarm.NIVEL_ALERTA.toLowerCase()}`}
                                                >
                                                    {alarm.NIVEL_ALERTA}
                                                </span>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    <div className="pagination">
                        <span>
                            Página {currentPage} de {totalPages}
                        </span>

                        <div>
                            <button
                                onClick={() => setPage((previous) => Math.max(1, previous - 1))}
                                disabled={currentPage === 1}
                            >
                                Anterior
                            </button>

                            <button
                                onClick={() => setPage((previous) => Math.min(totalPages, previous + 1))}
                                disabled={currentPage === totalPages}
                            >
                                Siguiente
                            </button>
                        </div>
                    </div>

                </section>

            </main>
        </div>
    );
}

export default App;