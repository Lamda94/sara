import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sara.config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga modelos ML al arrancar y libera recursos al cerrar."""
    logger.info("Iniciando Sara - Agente de Voz")
    logger.info("Cargando modelos ML (esto puede tardar la primera vez)...")

    # Pre-cargar modelos para evitar latencia en la primera petición
    from sara.services.stt_service import stt_service
    from sara.services.speaker_service import speaker_service

    stt_service._load_model()
    speaker_service._load_model()

    logger.info("Modelos cargados. Sara está lista.")
    yield
    logger.info("Sara apagándose...")


app = FastAPI(
    title="Sara - Agente de Voz",
    description="API de reconocimiento de hablante y agente conversacional por voz",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from sara.api.router import api_router, ws_router

app.include_router(api_router)
app.include_router(ws_router)
