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
    """Inicia la aplicación. Los modelos ML se cargan bajo demanda."""
    logger.info("Iniciando Sara - Agente de Voz")
    logger.info("Modelos ML se cargarán bajo demanda en la primera petición.")
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
