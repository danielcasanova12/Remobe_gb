import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Inicializa o MediaPipe Face Detection com um modelo otimizado para curtas distâncias (< 2m)
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

def detect_face_from_bytes(image_bytes: bytes) -> Optional[Tuple[int, int, int, int]]:
    """
    Detecta a face principal em uma imagem usando MediaPipe Face Detection.

    Args:
        image_bytes: A imagem em formato de bytes.

    Returns:
        Uma tupla com as coordenadas (x, y, w, h) da face detectada,
        ou None se nenhuma face for encontrada.
    """
    try:
        # Decodificar os bytes da imagem para um array numpy
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            logger.error("Falha ao decodificar a imagem para detecção de face.")
            return None

        # MediaPipe espera imagens em RGB, mas o OpenCV carrega em BGR
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        results = face_detection.process(image_rgb)

        if not results.detections:
            return None

        detection = results.detections[0]
        
        ih, iw, _ = image.shape
        bbox = detection.location_data.relative_bounding_box
        
        x, y, w, h = int(bbox.xmin * iw), int(bbox.ymin * ih), int(bbox.width * iw), int(bbox.height * ih)

        return (max(0, x), max(0, y), w, h)

    except Exception as e:
        logger.error(f"Erro durante a detecção de face com MediaPipe: {str(e)}", exc_info=True)
        return None
