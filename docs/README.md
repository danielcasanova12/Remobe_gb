# FastAPI Image Processor

## Setup local

### PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

### Windons
```powershell
python -m venv .venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt



run 
.\venv\Scripts\Activate.ps1
python -m uvicorn src.main:app --reload
```


### Bash
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

## Testes
```powershell
pytest
```

## Endpoints principais
- /api/v1/crop-round/
- /api/v1/remove-bg/{model}
- /api/v1/remove-bg-crop/{model}
- /api/v1/remove-bg-and-crop-round/
- /health

## Modelos suportados
- isnet
- u2net
- u2netp  
- u2net_human_seg
- u2net_cloth_seg
- u2net_custom
- silueta
- birefnet-general
- birefnet-general-lite
- birefnet-portrait

## Exemplos cURL

### Crop round
```bash
curl -X POST "http://localhost:8000/api/v1/crop-round/" -F "file=@test.png" --output result.png
```
*Nota: Este endpoint agora funciona mesmo se não detectar faces, usando um fallback inteligente que recorta o centro da imagem.*

### Remove background (birefnet-general)
```bash
curl -X POST "http://localhost:8000/api/v1/remove-bg/birefnet-general" -F "file=@test.png" --output result.png
```

### Legado: remove fundo e recorta retrato composto
```bash
curl -X POST "http://localhost:8000/api/v1/remove-bg-and-crop-round/?model=birefnet-general&radius_scale=1.8&vertical_bias=0.25" -F "file=@test.png" --output result.png
```
