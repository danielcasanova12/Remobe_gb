from rembg import new_session, remove
from functools import lru_cache
from typing import Any

@lru_cache(maxsize=8)
def get_session(model_key: str) -> Any:
    return new_session(model_key)

def remove_bg(image_bytes: bytes, model_key: str) -> bytes:
    session = get_session(model_key)
    try:
        output = remove(image_bytes, session=session)
        return output
    except Exception as e:
        raise RuntimeError(f"Erro ao remover fundo: {str(e)}")
