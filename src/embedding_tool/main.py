import os
import time

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Embeddings API", description="API for generating text embeddings", version="1.0.0")
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)


class EmbeddingRequest(BaseModel):
    text: str = Field(..., description="Text to generate embeddings for")


class EmbeddingResponse(BaseModel):
    embedding: list = Field(..., description="Generated embedding vector")
    processing_time: float = Field(..., description="Time taken to generate embeddings (seconds)")

class SearchEmbeddingResponse(EmbeddingResponse):
    text: str


@app.post("/embed", response_model=EmbeddingResponse)
async def get_embedding(request: EmbeddingRequest):
    """Generate embeddings for the provided text"""
    start_time = time.time()

    try:
        embedding = model.encode(request.text).tolist()
        processing_time = time.time() - start_time

        return EmbeddingResponse(embedding=embedding, processing_time=processing_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}") from e


@app.post("/search", response_model=SearchEmbeddingResponse)
async def search_document():
    pass


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": MODEL_NAME}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
