import pytest
from fastapi.testclient import TestClient
from src.main import app
from PIL import Image
import io

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# ...demais funções de teste...

def test_crop_round():
    img = Image.new("RGB", (128, 128), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    response = client.post("/api/v1/crop-round/", files={"file": ("test.png", buf, "image/png")})
    assert response.status_code in [200, 404, 400]  # Aceita face não encontrada