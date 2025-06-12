# NFT Collection Resolver API

A FastAPI-based service for resolving NFT collection names to their canonical information and contract addresses.

## Features

- Resolve NFT collection names using fuzzy matching
- Look up collections by contract address
- Get collection information by slug
- List all available collections
- Automatic API documentation with Swagger UI and ReDoc

## API Endpoints

- `GET /`: Root endpoint with API information
- `GET /resolve/{collection_name}`: Resolve a collection name to its canonical information
- `GET /collections`: Get all available collections
- `GET /collections/{slug}`: Get collection information by slug

## Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`

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