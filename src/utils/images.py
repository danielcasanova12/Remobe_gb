from PIL import Image, ImageDraw
from typing import Tuple
import numpy as np

def crop_to_round_centered_on_face(pil_image: Image.Image, face_coords: Tuple[int, int, int, int], radius_scale: float = 1.9) -> Image.Image:
    """
    Recorta uma imagem em formato circular com a face centralizada no círculo.
    
    Args:
        pil_image: Imagem PIL
        face_coords: Coordenadas da face (x, y, w, h)
        radius_scale: Escala para o tamanho do círculo em relação ao tamanho da face
    
    Returns:
        Image.Image: Imagem circular com a face centralizada
    """
    x, y, w, h = face_coords
    
    # Centro da face detectada
    face_center_x = x + w // 2
    face_center_y = y + h // 2
    
    # Calcular o raio baseado no tamanho da face
    face_size = max(w, h)
    radius = int(face_size * radius_scale)
    
    # Garantir que o círculo não ultrapasse os limites da imagem
    # Calcular o raio máximo possível mantendo a face no centro
    max_radius_from_face_x = min(face_center_x, pil_image.width - face_center_x)
    max_radius_from_face_y = min(face_center_y, pil_image.height - face_center_y)
    max_possible_radius = min(max_radius_from_face_x, max_radius_from_face_y)
    
    # Usar o menor entre o raio desejado e o máximo possível
    final_radius = min(radius, max_possible_radius)
    
    # Calcular os limites do crop quadrado centrado na face
    left = face_center_x - final_radius
    upper = face_center_y - final_radius
    right = face_center_x + final_radius
    lower = face_center_y + final_radius
    
    # Garantir que as coordenadas estão dentro dos limites da imagem
    left = max(0, left)
    upper = max(0, upper)
    right = min(pil_image.width, right)
    lower = min(pil_image.height, lower)
    
    # Recortar a região quadrada
    cropped = pil_image.crop((left, upper, right, lower))
    
    # Se o recorte não for perfeitamente quadrado devido aos limites da imagem,
    # criar uma nova imagem quadrada com fundo transparente
    crop_width = right - left
    crop_height = lower - upper
    
    if crop_width != crop_height:
        # Criar uma nova imagem quadrada
        square_size = max(crop_width, crop_height)
        square_image = Image.new("RGBA", (square_size, square_size), (0, 0, 0, 0))
        
        # Calcular onde posicionar a imagem recortada para manter a face centralizada
        paste_x = (square_size - crop_width) // 2
        paste_y = (square_size - crop_height) // 2
        
        square_image.paste(cropped, (paste_x, paste_y))
        cropped = square_image
    
    # Criar máscara circular
    size = cropped.size[0]  # Agora é garantidamente quadrada
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    # Aplicar a máscara circular
    result = cropped.copy()
    if result.mode != "RGBA":
        result = result.convert("RGBA")
    result.putalpha(mask)
    
    return result

def crop_round_portrait_composed(pil_image: Image.Image, face_coords: Tuple[int, int, int, int], radius_scale: float = 1.8, vertical_bias: float = 0.25, extra_margin_ratio: float = 0.30) -> Image.Image:
    x, y, w, h = face_coords
    cx, cy = x + w // 2, y + int(h * vertical_bias)
    radius = int(max(w, h) * radius_scale)
    margin = int(radius * extra_margin_ratio)
    left = max(cx - radius - margin, 0)
    upper = max(cy - radius - margin, 0)
    right = min(cx + radius + margin, pil_image.width)
    lower = min(cy + radius + margin, pil_image.height)
    cropped = pil_image.crop((left, upper, right, lower))
    mask = Image.new("L", cropped.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, cropped.size[0], cropped.size[1]), fill=255)
    result = cropped.copy()
    result.putalpha(mask)
    return result
