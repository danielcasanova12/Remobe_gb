import cv2
import numpy as np
from typing import Tuple, Optional
import io

HAARCASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    image = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(image, cv2.IMREAD_COLOR)

def detect_face(gray: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    face_cascade = cv2.CascadeClassifier(HAARCASCADE_PATH)
    if face_cascade.empty():
        raise RuntimeError("Erro ao carregar Haarcascade.")
    
    # Try multiple scale factors for better detection
    for scale_factor in [1.05, 1.1, 1.2, 1.3]:
        for min_neighbors in [3, 4, 5, 6]:
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=scale_factor, 
                minNeighbors=min_neighbors,
                minSize=(30, 30),  # Minimum face size
                maxSize=(300, 300)  # Maximum face size
            )
            if len(faces) > 0:
                # Return the largest face found
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                return tuple(largest_face)
    
    return None

def detect_face_from_bytes(image_bytes: bytes) -> Optional[Tuple[int, int, int, int]]:
    image = decode_image_bytes(image_bytes)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return detect_face(gray)
