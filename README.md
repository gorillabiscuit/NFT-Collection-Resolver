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
git clone <repository-url>
cd NFT_Collection_resolution
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

[Add your license here] 