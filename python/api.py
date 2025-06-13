from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from collection_resolver import NFTCollectionResolver, CollectionResolutionResult

app = FastAPI(
    title="NFT Collection Resolver API",
    description="API for resolving NFT collection names to their canonical information and contract addresses",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",     # React default port
    "http://localhost:8000",     # Development server
    "http://localhost:8080",     # Alternative development port
    "http://127.0.0.1:3000",    # React with IP
    "http://127.0.0.1:8000",    # Development with IP
    "http://127.0.0.1:8080",    # Alternative development with IP
    "https://nft-collection-resolver.onrender.com",  # Production API
    "*"  # Allow all origins (you might want to restrict this in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the resolver
resolver = NFTCollectionResolver("collections.json")

class ResolutionResponse(BaseModel):
    success: bool
    contract_address: Optional[str] = None
    canonical_name: Optional[str] = None
    slug: Optional[str] = None
    confidence_score: float = 0.0
    resolution_method: str = ""
    alternatives: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "NFT Collection Resolver API"}

@app.get("/resolve/{collection_name}", response_model=ResolutionResponse)
async def resolve_collection(collection_name: str):
    """
    Resolve an NFT collection name to its canonical information.
    
    - **collection_name**: The name, alias, or contract address of the collection to resolve
    """
    result = resolver.resolve_collection(collection_name)
    return result

@app.get("/collections")
async def get_all_collections():
    """
    Get a list of all available collections.
    """
    return resolver.get_all_collections()

@app.get("/collections/{slug}")
async def get_collection_by_slug(slug: str):
    """
    Get collection information by its slug.
    
    - **slug**: The unique identifier (slug) of the collection
    """
    collection = resolver.get_collection_by_slug(slug)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 