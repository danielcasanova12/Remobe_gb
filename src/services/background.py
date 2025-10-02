from rembg import new_session, remove
from functools import lru_cache
from typing import Any
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

@lru_cache(maxsize=8)
def get_session(model_key: str) -> Any:
    """
    Cria e cacheia uma sessão do rembg, deixando a biblioteca
    gerenciar o download e o cache dos modelos.
    """
    logger.info(f"Carregando modelo padrão '{model_key}' via rembg.")
    return new_session(model_key, providers=settings.ONNX_PROVIDERS)

def remove_bg(image_bytes: bytes, model_key: str) -> bytes:
    session = get_session(model_key)
    try:
        output = remove(image_bytes, session=session)
        return output
    except Exception as e:
        logger.error(f"Erro durante a remoção de fundo com o modelo '{model_key}': {e}", exc_info=True)
        raise RuntimeError(f"Erro ao remover fundo: {e}")
