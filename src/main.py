from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.core.config import settings
from src.core.logging import setup_logging
from src.api.v1.endpoints.image import router as image_router
from src.models.schemas import HealthResponse, RootResponse
from fastapi.responses import JSONResponse
import os

setup_logging()
app = FastAPI(
    title=settings.APP_NAME,
    description="API para processamento de imagens (remoção de fundo, recorte, etc)",
    version="1.0.0",
)

# Configurar arquivos estáticos para servir imagens temporárias
TEMP_DIR = "temp_images"
os.makedirs(TEMP_DIR, exist_ok=True)
app.mount(
    "/static/temp_images", StaticFiles(directory=TEMP_DIR), name="temp_images"
)

app.include_router(image_router, prefix=settings.API_V1_PREFIX, tags=["Image"])

@app.get("/", response_model=RootResponse, summary="Informações da API")
def root():
    return RootResponse(
        message="API de processamento de imagens",
        endpoints=[
            "/api/v1/crop-round/",
            "/api/v1/remove-bg/{model}",
            "/api/v1/remove-bg-crop/{model}",
            "/api/v1/process-url/",
            "/api/v1/remove-bg-and-crop-round/",
            "/health",
        ],
        models=[
            "u2net",
            "u2netp",
            "u2net_human_seg",
            "u2net_cloth_seg",
            "isnet-general-use",
            "isnet-anime",
            "birefnet-general",
            "birefnet-general-lite",
            "birefnet-portrait",
            "birefnet-dis",
            "birefnet-massive",
            "silueta",
            "bria-rmbg",
            "sam",
        ],
    )

@app.get("/health", response_model=HealthResponse, summary="Healthcheck")
def health():
    return HealthResponse(status="ok")
