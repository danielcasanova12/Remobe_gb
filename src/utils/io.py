from PIL import Image
import io

def bytes_to_png_rgba(pil_image: Image.Image) -> bytes:
    """Convert PIL Image to PNG bytes"""
    output = io.BytesIO()
    pil_image.save(output, format="PNG")
    return output.getvalue()
