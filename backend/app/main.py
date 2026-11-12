from fastapi import FastAPI
from app.api.alarms import router as alarms_router
from fastapi.middleware.cors import CORSMiddleware

# Inicialización de la aplicación
app = FastAPI(
    title="HITSS - Alarmas API",
    description="API para la gestión y clasificación de alarmas",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)



app.include_router(
    alarms_router,
    prefix="/api/alarms",
    tags=["Alarmas"]
)



@app.get("/", tags=["Inicio"])
def home():
    """
    Endpoint principal de la aplicación.
    """
    return {
        "message": "Bienvenido a HITSS Alarmas API",
        "status": "online"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Comprueba que el servidor esté funcionando.
    """
    return {
        "status": "ok",
        "application": "HITSS Alarmas"
    }