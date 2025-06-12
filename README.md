# NFT Collection Resolver API

A FastAPI-based service for resolving NFT collection names to their canonical information and contract addresses.

## Features

- Resolve NFT collection names using fuzzy matching
- Look up collections by contract address
- Get collection information by slug
- List all available collections
- Automatic API documentation with Swagger UI and ReDoc

## API Documentation

### Base URL
```
https://nft-collection-resolver.onrender.com
```

### Authentication
This API is currently public and does not require authentication.

### Endpoints

#### 1. Root Endpoint
```
GET /
```
Returns basic API information.

**Response:**
```json
{
    "message": "NFT Collection Resolver API"
}
```

#### 2. Resolve Collection
```
GET /resolve/{collection_name}
```
Resolves a collection name, alias, or contract address to its canonical information.

**Parameters:**
- `collection_name` (path parameter): The name, alias, or contract address to resolve

**Response:**
```json
{
    "success": true,
    "contract_address": "0x...",
    "canonical_name": "Collection Name",
    "slug": "collection-slug",
    "confidence_score": 1.0,
    "resolution_method": "exact",
    "alternatives": null,
    "error_message": null,
    "metadata": {
        // Additional collection metadata
    }
}
```

**Example Requests:**
```bash
# Resolve by name
curl https://nft-collection-resolver.onrender.com/resolve/bored%20ape

# Resolve by contract address
curl https://nft-collection-resolver.onrender.com/resolve/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d

# Resolve by alias
curl https://nft-collection-resolver.onrender.com/resolve/bayc
```

#### 3. Get All Collections
```
GET /collections
```
Returns a list of all available collections.

**Response:**
```json
[
    {
        "name": "Collection Name",
        "slug": "collection-slug",
        "contract_address": "0x...",
        "aliases": ["alias1", "alias2"],
        "metadata": {
            // Collection metadata
        }
    },
    // ... more collections
]
```

#### 4. Get Collection by Slug
```
GET /collections/{slug}
```
Returns detailed information about a specific collection.

**Parameters:**
- `slug` (path parameter): The unique identifier of the collection

**Response:**
```json
{
    "name": "Collection Name",
    "slug": "collection-slug",
    "contract_address": "0x...",
    "aliases": ["alias1", "alias2"],
    "metadata": {
        // Collection metadata
    }
}
```

### Error Responses

The API uses standard HTTP status codes:

- `200 OK`: Request successful
- `404 Not Found`: Collection not found
- `405 Method Not Allowed`: Invalid HTTP method
- `500 Internal Server Error`: Server error

Error response format:
```json
{
    "success": false,
    "error_message": "Error description",
    "alternatives": [
        // Suggested alternatives if available
    ]
}
```

### Interactive Documentation

The API provides interactive documentation through:
- Swagger UI: `https://nft-collection-resolver.onrender.com/docs`
- ReDoc: `https://nft-collection-resolver.onrender.com/redoc`

### Example Usage

#### Using cURL
```bash
# Resolve a collection
curl https://nft-collection-resolver.onrender.com/resolve/bored%20ape

# Get all collections
curl https://nft-collection-resolver.onrender.com/collections

# Get specific collection
curl https://nft-collection-resolver.onrender.com/collections/bored-ape-yacht-club
```

#### Using Python
```python
import requests

BASE_URL = "https://nft-collection-resolver.onrender.com"

# Resolve a collection
response = requests.get(f"{BASE_URL}/resolve/bored ape")
collection = response.json()

# Get all collections
response = requests.get(f"{BASE_URL}/collections")
collections = response.json()

# Get specific collection
response = requests.get(f"{BASE_URL}/collections/bored-ape-yacht-club")
collection = response.json()
```

#### Using JavaScript/TypeScript
```javascript
const BASE_URL = "https://nft-collection-resolver.onrender.com";

// Resolve a collection
async function resolveCollection(name) {
    const response = await fetch(`${BASE_URL}/resolve/${encodeURIComponent(name)}`);
    return await response.json();
}

// Get all collections
async function getAllCollections() {
    const response = await fetch(`${BASE_URL}/collections`);
    return await response.json();
}

// Get specific collection
async function getCollection(slug) {
    const response = await fetch(`${BASE_URL}/collections/${slug}`);
    return await response.json();
}
```

### Rate Limiting
The API is currently running on Render's free tier, which has some limitations:
- Services spin down after 15 minutes of inactivity
- First request after inactivity might be slow (cold start)
- Limited to 750 hours of runtime per month

### Best Practices
1. Always handle potential errors in your requests
2. Use appropriate HTTP methods
3. URL-encode collection names and slugs
4. Cache responses when possible to reduce API calls
5. Implement retry logic for failed requests

## Development

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Clone the repository:
```bash
git clone git@github.com:gorillabiscuit/NFT-Collection-Resolver.git
cd NFT-Collection-Resolver
```

2. Install dependencies:
```bash
pip install -r python/requirements.txt
```

3. Run the development server:
```bash
python python/api.py
```

The API will be available at `http://localhost:8000`

## Deployment

This project is configured for deployment on Render.com. The deployment is managed through the `render.yaml` configuration file.

## License

MIT License

Copyright (c) 2024 gorillabiscuit

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 