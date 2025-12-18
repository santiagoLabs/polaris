from openai import AsyncOpenAI
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-3-small"
    
    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            input = text,
            model = self.model,
            dimensions = 1536,
        )

        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            input = texts, 
            model = self.model, 
            dimensions = 1536,
        )

        return [item.embedding for item in response.data]
    
embedding_service = EmbeddingService()