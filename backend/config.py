import os
from pydantic import BaseModel

class Settings(BaseModel):
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    qdrant_endpoint: str = os.getenv("QDRANT_ENDPOINT", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
        
settings = Settings()
