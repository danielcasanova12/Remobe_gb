from PIL import Image, ImageDraw
from typing import Tuple
import numpy as np

def crop_to_round_centered_on_face(pil_image: Image.Image, face_coords: Tuple[int, int, int, int], radius_scale: float = 1.5, vertical_bias: float = 0.35, output_size: Tuple[int, int] = (512, 512)) -> Image.Image:
    """
    Recorta uma área quadrada ao redor da face, redimensiona para o tamanho de saída,
    e então aplica uma máscara circular, preenchendo os cantos com branco.
    
    Args:
        pil_image: Imagem PIL
        face_coords: Coordenadas da face (x, y, w, h)
        radius_scale: Escala para o raio do círculo em relação ao tamanho da face.
        vertical_bias: Ajuste vertical para o centro do recorte (0.5 = centro, < 0.5 = para cima).
        output_size: O tamanho final (largura, altura) da imagem de saída.

    Returns:
        Image.Image: Imagem quadrada com recorte circular e fundo branco.
    """
    # 1. Recorta um quadrado centrado na face
    cropped_square = crop_to_square_centered_on_face(
        pil_image, face_coords, vertical_bias=vertical_bias, radius_scale=radius_scale, output_size=output_size
    )

    # 2. Criar máscara circular para a imagem já redimensionada
    mask = Image.new("L", output_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, output_size[0], output_size[1]), fill=255)

    # 3. Criar fundo branco e colar a imagem recortada usando a máscara
    final_image = Image.new("RGB", output_size, (255, 255, 255))
    final_image.paste(cropped_square, (0, 0), mask)

    return final_image

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

def draw_face_on_image(pil_image: Image.Image, face_coords: Tuple[int, int, int, int]) -> Image.Image:
    """
    Desenha um retângulo vermelho ao redor da face detectada em uma cópia da imagem.

    Args:
        pil_image (Image.Image): A imagem original.
        face_coords (Tuple[int, int, int, int]): As coordenadas (x, y, w, h) da face.

    Returns:
        Image.Image: Uma nova imagem com o retângulo desenhado.
    """
    debug_image = pil_image.copy()
    draw = ImageDraw.Draw(debug_image)
    x, y, w, h = face_coords
    draw.rectangle([x, y, x + w, y + h], outline="red", width=5)
    return debug_image

def crop_to_square_centered_on_face(pil_image: Image.Image, face_coords: Tuple[int, int, int, int], vertical_bias: float = 0.35, radius_scale: float = 1.5, output_size: Tuple[int, int] = (512, 512)) -> Image.Image:
    """
    Recorta uma área quadrada ao redor da face e a redimensiona para o tamanho de saída.

    Args:
        pil_image: Imagem PIL.
        face_coords: Coordenadas da face (x, y, w, h).
        vertical_bias: Ajuste vertical para o centro do recorte.
        radius_scale: Fator para determinar o tamanho do recorte ao redor da face.
        output_size: O tamanho final (largura, altura) da imagem de saída.

    Returns:
        Image.Image: Imagem quadrada com a face centralizada.
    """
    x, y, w, h = face_coords

    # 1. Calcular o centro da face com viés vertical para melhor enquadramento
    face_center_x = x + w // 2
    face_center_y = y + int(h * vertical_bias)

    # 2. Calcular o "raio" do quadrado de recorte (metade do lado)
    face_size = max(w, h)
    crop_radius = int(face_size * radius_scale * 0.5)

    # 3. Definir os limites do quadrado de recorte
    left = face_center_x - crop_radius
    upper = face_center_y - crop_radius
    right = face_center_x + crop_radius
    lower = face_center_y + crop_radius

    # 4. Recortar a imagem original
    cropped_image = pil_image.crop((left, upper, right, lower))

    # 5. Redimensionar o quadrado recortado para o tamanho de saída final
    if cropped_image.size != output_size:
        cropped_image = cropped_image.resize(output_size, Image.Resampling.LANCZOS)

    # 6. Garantir que a imagem esteja em RGB (para consistência)
    if cropped_image.mode != "RGB":
        # Se for RGBA, colar em um fundo branco para remover a transparência
        if cropped_image.mode == "RGBA":
            rgb_image = Image.new("RGB", cropped_image.size, (255, 255, 255))
            rgb_image.paste(cropped_image, mask=cropped_image.split()[3]) # 3 é o canal alfa
            return rgb_image
        return cropped_image.convert("RGB")

    return cropped_image
