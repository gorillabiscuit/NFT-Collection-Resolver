# NFT Collection Resolver

A robust Python tool for resolving user-provided NFT collection names (including typos, abbreviations, and colloquial terms) to canonical collection information and contract addresses.

## Overview

The NFT Collection Resolver helps normalize user input for NFT collections by mapping various forms of collection references to their canonical information. It handles:

- **Exact matches**: "CryptoPunks", "BAYC" 
- **Fuzzy matches**: "Bored Ape Yatch Club" (typo correction)
- **Contract addresses**: "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d"
- **Abbreviations**: "MAYC" → Mutant Ape Yacht Club
- **Colloquial terms**: "punk wrappers" → Wrapped CryptoPunks

## Features

### 🎯 **Multi-Strategy Resolution**
1. **Contract Address Lookup** - Direct contract address resolution
2. **Exact Matching** - Fast dictionary lookup for known names/aliases  
3. **Fuzzy String Matching** - Typo-tolerant similarity matching

### 🔒 **Security & Validation**
- Input length limits (100 characters)
- Character whitelisting to prevent injection attacks
- Safe handling of malformed input

### ⚡ **Performance Optimized**
- LRU caching for repeated queries (maxsize=1000)
- O(1) dictionary lookups for exact matches
- < 50ms response time for most queries

### 🧠 **Intelligent Disambiguation**
- Popularity-based ranking for ambiguous matches
- Alternative suggestions for failed matches
- Confidence scoring for match quality

## Installation

1. Clone or extract this folder
2. Install optional dependencies for better performance:

```bash
pip install -r requirements.txt
```

**Note**: The `rapidfuzz` library is optional but recommended for improved fuzzy matching performance. If not installed, the resolver will use a fallback implementation.

## Quick Start

```python
from collection_resolver import NFTCollectionResolver

# Initialize the resolver
resolver = NFTCollectionResolver("collections.json")

# Resolve a collection
result = resolver.resolve_collection("BAYC")

if result.success:
    print(f"Collection: {result.canonical_name}")
    print(f"Contract: {result.contract_address}")
    print(f"Confidence: {result.confidence_score}")
else:
    print(f"Error: {result.error_message}")
    if result.alternatives:
        print("Suggestions:", [alt['name'] for alt in result.alternatives])
```

## Example Usage

Run the included example script to see the resolver in action:

```bash
python example_usage.py
```

This will demonstrate:
- Exact name matching
- Alias resolution 
- Contract address lookup
- Fuzzy matching for typos
- Ambiguity handling
- Error cases and suggestions

## API Reference

### Core Classes

#### `NFTCollectionResolver`

**Constructor:**
```python
NFTCollectionResolver(json_file_path: str)
```

**Main Methods:**

```python
def resolve_collection(self, user_input: str) -> CollectionResolutionResult:
    """
    Resolve user input to canonical collection information.
    
    Returns CollectionResolutionResult with:
    - success: bool
    - canonical_name: str
    - contract_address: str  
    - slug: str
    - confidence_score: float (0.0-1.0)
    - resolution_method: str ("exact", "fuzzy", "contract_address")
    - alternatives: List[Dict] (for ambiguous/failed matches)
    - error_message: str (when success=False)
    - metadata: Dict (additional collection info)
    """

def get_collection_by_slug(self, slug: str) -> Optional[Dict]:
    """Get collection data by slug."""

def get_all_collections(self) -> List[Dict]:
    """Get all collection data."""

def refresh_data(self, json_file_path: str):
    """Reload collection data from JSON file."""
```

#### `CollectionResolutionResult`

Data class containing resolution results:

```python
@dataclass
class CollectionResolutionResult:
    success: bool
    contract_address: Optional[str] = None
    canonical_name: Optional[str] = None
    slug: Optional[str] = None
    confidence_score: float = 0.0
    resolution_method: str = ""
    alternatives: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

## Data Format

The resolver uses a JSON file (`collections.json`) with the following structure:

```json
{
  "version": "1.1",
  "last_updated": "2024-12-19",
  "description": "NFT Collection metadata for name resolution",
  "collections": [
    {
      "name": "CryptoPunks",
      "slug": "cryptopunks", 
      "contract_address": "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb",
      "chain": "ethereum",
      "aliases": ["punks", "cp", "cryptopunk"],
      "wrapper_contracts": ["0xb7f7f6c52f2e2fdb1963eab30438024864c313f6"],
      "group_id": "cryptopunks",
      "category": "pfp",
      "metadata": {
        "opensea_slug": "cryptopunks",
        "verified": true,
        "popularity_rank": 1,
        "description": "10,000 unique collectible characters..."
      }
    }
  ]
}
```

### Required Fields
- `name`: Canonical collection name
- `slug`: Unique identifier slug
- `contract_address`: Ethereum contract address
- `aliases`: Array of alternative names/abbreviations

### Optional Fields
- `wrapper_contracts`: Array of wrapper contract addresses
- `id_ranges`: Token ID ranges for collections with sub-ranges
- `group_id`: Grouping identifier for related collections
- `category`: Collection category (pfp, art, gaming, etc.)
- `metadata`: Additional metadata (popularity, verification, etc.)

## Resolution Strategies

### 1. Contract Address Resolution
- Validates Ethereum address format (`0x` + 40 hex characters)
- Direct lookup in contract address index
- Returns canonical collection info for known contracts

### 2. Exact Matching
- Case-insensitive lookup in pre-built index
- Matches canonical names, aliases, and slugs
- O(1) performance with immediate results

### 3. Fuzzy String Matching
- Uses string similarity algorithms (rapidfuzz or fallback)
- Configurable similarity threshold (default: 0.8)
- Handles typos, abbreviations, and variations
- Popularity-based disambiguation for close matches

## Error Handling

The resolver handles various error conditions gracefully:

### Input Validation Errors
- Empty input
- Input too long (>100 characters)
- Invalid characters

### Resolution Failures
- No matching collections found
- Ambiguous queries (multiple equally-likely matches)
- Contract address not in database

### System Errors  
- Missing or corrupted data file
- JSON parsing errors
- File system issues

All errors return a `CollectionResolutionResult` with `success=False` and descriptive error messages.

## Performance Characteristics

- **Exact matches**: O(1) - immediate dictionary lookup
- **Contract addresses**: O(1) - direct index lookup  
- **Fuzzy matching**: O(n) - scales with collection count
- **Memory usage**: ~1-5MB for typical collection databases
- **Response time**: <50ms for most queries, <200ms for complex fuzzy matches

## Customization

### Adjusting Fuzzy Threshold
```python
resolver = NFTCollectionResolver("collections.json")
resolver.fuzzy_threshold = 0.7  # Lower threshold = more permissive matching
```

### Adding New Collections
Edit the `collections.json` file to add new collections following the schema.

### Custom Popularity Ranking
Collections with lower `popularity_rank` values get slight preference in ambiguous matches.

## Use Cases

### NFT Lending Platforms
- Normalize collateral collection names
- Validate collection contracts
- Handle user input variations

### NFT Marketplaces  
- Search auto-completion
- Collection name standardization
- User experience improvements

### Data Analytics
- Collection name normalization across datasets
- Consistent collection identification
- Data cleaning pipelines

### Chatbots & AI Assistants
- Natural language collection references
- User-friendly collection lookup
- Conversational NFT interfaces

## Limitations

1. **Coverage**: Only includes collections in the JSON database
2. **Language**: Primarily English collection names and aliases
3. **Blockchain**: Currently focused on Ethereum collections
4. **Real-time**: Data is static; requires manual updates for new collections

## Contributing

To add new collections or improve existing data:

1. Edit `collections.json` following the schema
2. Add canonical names, aliases, and metadata
3. Test with the example script
4. Ensure contract addresses are accurate

## License

This tool is provided as-is for educational and development purposes. Please verify all contract addresses and collection information independently before use in production systems.

## Support

For questions or issues with this resolver:
1. Check the example usage script
2. Verify your JSON data format
3. Test with known collections first
4. Review error messages for debugging hints 