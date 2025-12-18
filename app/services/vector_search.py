from app.db.connection import db
from app.services.embeddings import embedding_service

async def find_similar_events(text: str, limit: int = 5) -> list[dict]:
    embedding = await embedding_service.embed(text)
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
    
    rows = await db.fetch(f"""
        SELECT id, text, 1-(embedding <=> '{embedding_str}'::vector) as similarity
        FROM events
        ORDER BY embedding <=> '{embedding_str}'::vector
        LIMIT {limit}
        """
    )
    
    return [
        {
            "id": str(row["id"]),
            "text": row["text"],
            "similarity": round(row["similarity"], 3),
        }
        for row in rows
    ]