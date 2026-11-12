const API_BASE_URL = "http://127.0.0.1:8000";

// Procesar respuestas HTTP.
async function handleResponse(response) {
    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || `Error del servidor: ${response.status}`
        );
    }

    return data;
}

// Consultar el estado del backend.
export async function checkApiHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse(response);
}

// Importar un archivo CSV.
export async function importAlarms(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
        `${API_BASE_URL}/api/alarms/import`,
        {
            method: "POST",
            body: formData
        }
    );

    return handleResponse(response);
}

// Consultar alarmas con filtro opcional.
export async function getAlarms(level = "") {
    const url = new URL(`${API_BASE_URL}/api/alarms/`);

    if (level) {
        url.searchParams.set("level", level);
    }

    const response = await fetch(url);
    return handleResponse(response);
}

// Exportar las alarmas que coinciden con el filtro.
export async function exportAlarms(level = "") {
    const url = new URL(`${API_BASE_URL}/api/alarms/export`);

    if (level) {
        url.searchParams.set("level", level);
    }

    const response = await fetch(url);

    if (!response.ok) {
        let message = "No fue posible exportar las alarmas.";

        try {
            const data = await response.json();
            message = data.detail || message;
        } catch {
            // Mantener el mensaje general si la respuesta no es JSON.
        }

        throw new Error(message);
    }

    const blob = await response.blob();

    if (blob.size === 0) {
        throw new Error("El archivo Excel está vacío.");
    }

    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = objectUrl;
    link.download = level
        ? `alarmas_${level}.xlsx`
        : "alarmas.xlsx";

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(objectUrl);

    return link.download;
}

// Consultar el resumen de alarmas del día.
export async function getTodaySummary() {
    const response = await fetch(
        `${API_BASE_URL}/api/alarms/summary/today`
    );

    return handleResponse(response);
}