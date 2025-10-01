from pydantic import BaseModel
from typing import List

class HealthResponse(BaseModel):
    status: str

class RootResponse(BaseModel):
    message: str
    endpoints: List[str]
    models: List[str]
