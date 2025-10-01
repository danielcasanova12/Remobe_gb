from fastapi import APIRouter, UploadFile, File, HTTPException, status, Request
from fastapi.responses import Response
from src.services.face import detect_face_from_bytes
from src.services.background import remove_bg
from src.utils.images import crop_to_round_centered_on_face, crop_round_portrait_composed
from src.utils.io import bytes_to_png_rgba
from PIL import Image
import io
import logging
import requests
import uuid
import os
from datetime import datetime, timedelta
from pydantic import BaseModel, HttpUrl
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)

# Diretório para armazenar temporariamente as imagens processadas
TEMP_DIR = "temp_images"
os.makedirs(TEMP_DIR, exist_ok=True)

# Modelos Pydantic
class ImageUrlRequest(BaseModel):
    image_url: HttpUrl
    model: str = "birefnet-general"

class ProcessedImageResponse(BaseModel):
    processed_image_url: str
    original_image_url: str
    model_used: str
    processed_at: str


@router.post("/crop-round/", summary="Recorta imagem em círculo centralizado na face")
async def crop_round(file: UploadFile = File(...), use_fallback: bool = True):
    """
    Recorta uma imagem em formato circular, centralizando na face detectada.
    Se nenhuma face for encontrada e use_fallback=True, usa o centro da imagem.
    """
    logger.info(f"Iniciando /crop-round para o arquivo: {file.filename}")
    if not file.content_type.startswith("image/"):
        logger.warning(f"Tipo de conteúdo inválido para /crop-round: {file.content_type}")
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem.")
    
    try:
        image_bytes = await file.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        
        # Tentar detectar face
        logger.debug("Tentando detectar face...")
        face_coords = detect_face_from_bytes(image_bytes)
        
        if not face_coords:
            logger.warning("Nenhuma face encontrada na imagem.")
            if not use_fallback:
                logger.error("Nenhuma face encontrada e fallback está desativado.")
                raise HTTPException(status_code=404, detail="Nenhuma face encontrada na imagem.")
            
            logger.info("Usando fallback para o centro da imagem.")
            # Se não encontrar face, usar o centro da imagem como fallback
            w, h = pil_image.size
            # Criar coordenadas de face fictícia centrada na imagem
            face_size = min(w, h) // 3  # Usar 1/3 da menor dimensão
            face_x = (w - face_size) // 2
            face_y = (h - face_size) // 2
            face_coords = (face_x, face_y, face_size, face_size)
            
        result = crop_to_round_centered_on_face(pil_image, face_coords)
        output_bytes = bytes_to_png_rgba(result)
        logger.info(f"Processamento de /crop-round para {file.filename} concluído com sucesso.")
        return Response(content=output_bytes, media_type="image/png")
        
    except HTTPException as http_exc:
        logger.error(f"HTTPException em /crop-round: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado em /crop-round para {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

# Endpoints de remoção de fundo
MODELS = [
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
    "sam"
]

def create_remove_bg_endpoint(model: str):
    async def endpoint(file: UploadFile = File(...), alpha_matting: bool = False, post_process_mask: bool = True):
        logger.info(f"Iniciando /remove-bg/{model} para o arquivo: {file.filename}")
        if not file.content_type.startswith("image/"):
            logger.warning(f"Tipo de conteúdo inválido para /remove-bg/{model}: {file.content_type}")
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem.")
        image_bytes = await file.read()
        try:
            logger.debug(f"Removendo fundo com o modelo {model}...")
            output_bytes = remove_bg(image_bytes, model_key=model)
            logger.info(f"Processamento de /remove-bg/{model} para {file.filename} concluído com sucesso.")
        except Exception as e:
            logger.error(f"Erro em /remove-bg/{model} para {file.filename}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Erro ao remover fundo: {str(e)}")
        return Response(content=output_bytes, media_type="image/png")
    return endpoint

def create_remove_bg_crop_endpoint(model: str):
    async def endpoint(file: UploadFile = File(...)):
        logger.info(f"Iniciando /remove-bg-crop/{model} para o arquivo: {file.filename}")
        if not file.content_type.startswith("image/"):
            logger.warning(f"Tipo de conteúdo inválido para /remove-bg-crop/{model}: {file.content_type}")
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem.")
        image_bytes = await file.read()
        try:
            logger.debug(f"Removendo fundo com o modelo {model}...")
            bg_removed = remove_bg(image_bytes, model_key=model)
            pil_image = Image.open(io.BytesIO(bg_removed)).convert("RGBA")
            logger.debug("Tentando detectar face para recorte...")
            face_coords = detect_face_from_bytes(image_bytes)
            if not face_coords:
                logger.error(f"Face não encontrada em /remove-bg-crop/{model} para {file.filename}.")
                raise HTTPException(status_code=404, detail="Face não encontrada.")
            logger.debug("Recortando imagem...")
            result = crop_to_round_centered_on_face(pil_image, face_coords)
            output_bytes = bytes_to_png_rgba(result)
            logger.info(f"Processamento de /remove-bg-crop/{model} para {file.filename} concluído com sucesso.")
        except HTTPException as http_exc:
            logger.error(f"HTTPException em /remove-bg-crop/{model}: {http_exc.detail}")
            raise
        except Exception as e:
            logger.error(f"Erro em /remove-bg-crop/{model} para {file.filename}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Erro ao remover fundo e recortar: {str(e)}")
        return Response(content=output_bytes, media_type="image/png")
    return endpoint

# Register endpoints for each model
for model in MODELS:
    router.add_api_route(
        f"/remove-bg/{model}",
        create_remove_bg_endpoint(model),
        methods=["POST"],
        summary=f"Remove fundo usando modelo {model}",
        response_class=Response
    )
    
    router.add_api_route(
        f"/remove-bg-crop/{model}",
        create_remove_bg_crop_endpoint(model),
        methods=["POST"],
        summary=f"Remove fundo e recorta em círculo usando modelo {model}",
        response_class=Response
    )

# Endpoint para processar imagem via URL
@router.post("/process-url/", response_model=ProcessedImageResponse, summary="Remove fundo de imagem via URL usando birefnet-general")
async def process_image_from_url(data: ImageUrlRequest, request: Request):
    """
    Baixa uma imagem de uma URL, remove o fundo usando o modelo especificado (padrão: birefnet-general),
    salva temporariamente e retorna um link para a imagem processada.
    """
    logger.info(f"Iniciando processamento via URL: {data.image_url} com modelo {data.model}")
    
    # Validar modelo
    if data.model not in MODELS:
        logger.error(f"Modelo não suportado: {data.model}")
        raise HTTPException(status_code=400, detail=f"Modelo '{data.model}' não suportado. Modelos disponíveis: {MODELS}")
    
    try:
        # Baixar imagem da URL
        logger.debug(f"Baixando imagem da URL: {data.image_url}")
        response = requests.get(str(data.image_url), timeout=30)
        response.raise_for_status()
        
        # Verificar se é uma imagem
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            logger.error(f"URL não aponta para uma imagem válida. Content-Type: {content_type}")
            raise HTTPException(status_code=400, detail="URL deve apontar para uma imagem válida")
        
        image_bytes = response.content
        logger.debug(f"Imagem baixada com sucesso. Tamanho: {len(image_bytes)} bytes")
        
        # Remover fundo usando o modelo especificado
        logger.debug(f"Removendo fundo com modelo: {data.model}")
        processed_bytes = remove_bg(image_bytes, model_key=data.model)
        
        # Gerar nome único para o arquivo
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"processed_{timestamp}_{unique_id}.png"
        file_path = os.path.join(TEMP_DIR, filename)
        
        # Salvar imagem processada
        with open(file_path, 'wb') as f:
            f.write(processed_bytes)
        
        logger.info(f"Imagem processada salva em: {file_path}")
        
        # Construir URL do arquivo processado (assumindo que será servido estaticamente)
        processed_url = request.url_for('temp_images', path=filename)
        
        # Criar resposta
        response_data = ProcessedImageResponse(
            processed_image_url=str(processed_url),
            original_image_url=str(data.image_url),
            model_used=data.model,
            processed_at=datetime.now().isoformat()
        )
        
        logger.info(f"Processamento via URL concluído com sucesso para: {data.image_url}")
        return response_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao baixar imagem da URL {data.image_url}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao baixar imagem: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado no processamento via URL {data.image_url}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

# Endpoint legado
@router.post("/remove-bg-and-crop-round/", summary="Remove fundo e recorta retrato composto (LEGADO)")
async def remove_bg_and_crop_round(file: UploadFile = File(...), model: str = "birefnet-general", radius_scale: float = 1.8, vertical_bias: float = 0.25):
    logger.info(f"Iniciando endpoint legado /remove-bg-and-crop-round/ para o arquivo: {file.filename} com modelo {model}")
    if not file.content_type.startswith("image/"):
        logger.warning(f"Tipo de conteúdo inválido para /remove-bg-and-crop-round/: {file.content_type}")
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem.")
    image_bytes = await file.read()
    if model not in MODELS:
        logger.error(f"Modelo não suportado '{model}' para /remove-bg-and-crop-round/.")
        raise HTTPException(status_code=400, detail="Modelo não suportado.")
    try:
        logger.debug(f"Removendo fundo com o modelo {model}...")
        bg_removed = remove_bg(image_bytes, model_key=model)
        pil_image = Image.open(io.BytesIO(bg_removed)).convert("RGBA")
        logger.debug("Tentando detectar face para recorte...")
        face_coords = detect_face_from_bytes(image_bytes)
        if not face_coords:
            logger.error(f"Face não encontrada em /remove-bg-and-crop-round/ para {file.filename}.")
            raise HTTPException(status_code=404, detail="Face não encontrada.")
        logger.debug("Recortando imagem (retrato composto)...")
        result = crop_round_portrait_composed(pil_image, face_coords, radius_scale=radius_scale, vertical_bias=vertical_bias)
        output_bytes = bytes_to_png_rgba(result)
        logger.info(f"Processamento de /remove-bg-and-crop-round/ para {file.filename} concluído com sucesso.")
    except HTTPException as http_exc:
        logger.error(f"HTTPException em /remove-bg-and-crop-round/: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Erro em /remove-bg-and-crop-round/ para {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao remover fundo e recortar: {str(e)}")
    return Response(content=output_bytes, media_type="image/png")
