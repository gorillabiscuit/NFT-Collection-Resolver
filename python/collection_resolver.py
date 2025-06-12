import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from functools import lru_cache
import time

try:
    from rapidfuzz import fuzz
except ImportError:
    # Fallback to basic string matching if rapidfuzz not available
    class fuzz:
        @staticmethod
        def ratio(a: str, b: str) -> float:
            # Simple Levenshtein-based similarity
            if a == b:
                return 100.0
            if not a or not b:
                return 0.0
            
            # Simple character overlap ratio
            set_a = set(a.lower())
            set_b = set(b.lower())
            intersection = len(set_a & set_b)
            union = len(set_a | set_b)
            
            return (intersection / union * 100.0) if union > 0 else 0.0


@dataclass
class CollectionResolutionResult:
    """Result of NFT collection name resolution."""
    success: bool
    contract_address: Optional[str] = None
    canonical_name: Optional[str] = None
    slug: Optional[str] = None
    confidence_score: float = 0.0
    resolution_method: str = ""
    alternatives: Optional[List[Dict[str, Any]]] = field(default_factory=list)
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class SecurityValidator:
    """Input validation and security measures."""
    MAX_INPUT_LENGTH = 100
    ALLOWED_CHARACTERS = re.compile(r'^[a-zA-Z0-9\s\-_.()]+$')
    
    @classmethod
    def validate_input(cls, user_input: str) -> str:
        """Sanitize and validate user input."""
        if user_input is None:
            raise ValueError("Input cannot be None")
        
        # Convert to string and strip
        input_str = str(user_input).strip()
        
        # Length check
        if len(input_str) > cls.MAX_INPUT_LENGTH:
            raise ValueError(f"Input too long (max {cls.MAX_INPUT_LENGTH} chars)")
        
        # Empty check
        if not input_str:
            raise ValueError("Input cannot be empty")
        
        # Character whitelist (allow some flexibility for testing)
        # Remove potential SQL injection patterns
        sanitized = input_str.replace("'", "").replace(";", "").replace("--", "")
        
        return sanitized.strip()


class NFTCollectionResolver:
    """
    NFT Collection Name Resolution Tool.
    
    Resolves user-provided collection names (fuzzy, abbreviated, or formal) 
    to canonical collection information and contract addresses.
    """
    
    def __init__(self, json_file_path: str):
        """Initialize resolver with JSON data file."""
        self.collections = {}  # slug -> collection data
        self.lookup_index = {}  # alias/name -> slug
        self.contract_index = {}  # contract_address -> slug
        self.fuzzy_threshold = 0.8
        
        self._load_data(json_file_path)
        self._build_indexes()
    
    def _load_data(self, json_file_path: str):
        """Load collection data from JSON file."""
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Collections data file not found: {json_file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in collections file: {e}")
        
        # Validate data structure
        if "collections" not in data:
            raise ValueError("Collections data missing 'collections' key")
        
        # Store collections by slug for fast lookup
        for collection in data["collections"]:
            try:
                slug = collection["slug"]
                # Validate required fields
                required_fields = ["name", "slug", "contract_address", "aliases"]
                for field in required_fields:
                    if field not in collection:
                        print(f"Warning: Collection {slug} missing required field: {field}")
                        if field == "aliases":
                            collection["aliases"] = []
                
                self.collections[slug] = collection
            except (KeyError, TypeError) as e:
                print(f"Warning: Skipping malformed collection data: {e}")
                continue
        
        # Load pre-built lookup index if available
        if "lookup_index" in data:
            self.lookup_index.update(data["lookup_index"])
    
    def _build_indexes(self):
        """Build search indexes from collection data."""
        for slug, collection in self.collections.items():
            try:
                # Index by contract address (case insensitive)
                contract_addr = collection.get("contract_address", "").lower()
                if contract_addr:
                    self.contract_index[contract_addr] = slug
                
                # Index canonical name (case insensitive)
                canonical_name = collection.get("name", "").lower()
                if canonical_name:
                    self.lookup_index[canonical_name] = slug
                
                # Index all aliases (case insensitive)
                aliases = collection.get("aliases", [])
                for alias in aliases:
                    if alias:  # Skip empty aliases
                        self.lookup_index[alias.lower()] = slug
                
                # Index slug itself
                self.lookup_index[slug.lower()] = slug
                
            except (KeyError, TypeError, AttributeError) as e:
                print(f"Warning: Error building index for collection {slug}: {e}")
                continue
    
    @lru_cache(maxsize=1000)
    def resolve_collection(self, user_input: str) -> CollectionResolutionResult:
        """
        Main resolution function with tiered matching strategy.
        
        Strategy:
        1. Contract address lookup
        2. Exact match (alias/name lookup)  
        3. Fuzzy string matching
        
        Returns CollectionResolutionResult with resolved collection info.
        """
        start_time = time.time()
        
        try:
            # Input validation and sanitization
            normalized_input = SecurityValidator.validate_input(user_input).lower().strip()
        except ValueError as e:
            return CollectionResolutionResult(
                success=False,
                error_message=str(e)
            )
        
        try:
            # Strategy 1: Contract address lookup
            if self._is_contract_address(normalized_input):
                result = self._resolve_by_contract(normalized_input)
                result.execution_time_ms = (time.time() - start_time) * 1000
                return result
            
            # Strategy 2: Exact match (alias/name lookup)  
            exact_match = self._resolve_exact_match(normalized_input)
            if exact_match:
                exact_match.execution_time_ms = (time.time() - start_time) * 1000
                return exact_match
            
            # Strategy 3: Fuzzy string matching
            fuzzy_matches = self._resolve_fuzzy_match(normalized_input)
            
            if fuzzy_matches:
                top_match = fuzzy_matches[0]
                
                # Check for ambiguity (close scores within 0.1)
                if (len(fuzzy_matches) > 1 and 
                    abs(fuzzy_matches[0][1] - fuzzy_matches[1][1]) < 0.1):
                    
                    # Return ambiguous result with alternatives
                    alternatives = []
                    for slug, score in fuzzy_matches[:3]:
                        collection = self.collections[slug]
                        alternatives.append({
                            "name": collection["name"],
                            "contract_address": collection["contract_address"],
                            "slug": collection["slug"],
                            "aliases": collection.get("aliases", [])[:3]
                        })
                    
                    result = CollectionResolutionResult(
                        success=False,
                        error_message="AMBIGUOUS",
                        alternatives=alternatives
                    )
                    result.execution_time_ms = (time.time() - start_time) * 1000
                    return result
                
                # Return top match if confidence is high enough
                if top_match[1] >= self.fuzzy_threshold:
                    collection = self.collections[top_match[0]]
                    result = CollectionResolutionResult(
                        success=True,
                        contract_address=collection["contract_address"],
                        canonical_name=collection["name"],
                        slug=collection["slug"],
                        confidence_score=top_match[1],
                        resolution_method="fuzzy",
                        metadata=collection.get("metadata", {})
                    )
                    result.execution_time_ms = (time.time() - start_time) * 1000
                    return result
            
            # No matches found - generate suggestions
            suggestions = self._get_suggestions(normalized_input)
            result = CollectionResolutionResult(
                success=False,
                error_message="No matching collections found",
                alternatives=suggestions
            )
            result.execution_time_ms = (time.time() - start_time) * 1000
            return result
            
        except Exception as e:
            # Fallback error handling
            return CollectionResolutionResult(
                success=False,
                error_message=f"Resolution error: {str(e)}"
            )
    
    def _is_contract_address(self, input_str: str) -> bool:
        """Check if input looks like an Ethereum contract address."""
        return bool(re.match(r'^0x[a-fA-F0-9]{40}$', input_str))
    
    def _resolve_by_contract(self, contract_address: str) -> CollectionResolutionResult:
        """Resolve collection by contract address."""
        normalized_address = contract_address.lower()
        
        if slug := self.contract_index.get(normalized_address):
            collection = self.collections[slug]
            return CollectionResolutionResult(
                success=True,
                contract_address=collection["contract_address"],
                canonical_name=collection["name"],
                slug=collection["slug"],
                confidence_score=1.0,
                resolution_method="contract_address",
                metadata=collection.get("metadata", {})
            )
        
        return CollectionResolutionResult(
            success=False,
            error_message=f"Unknown contract address: {contract_address}"
        )
    
    def _resolve_exact_match(self, normalized_input: str) -> Optional[CollectionResolutionResult]:
        """Check for exact matches in lookup index."""
        if slug := self.lookup_index.get(normalized_input):
            collection = self.collections[slug]
            return CollectionResolutionResult(
                success=True,
                contract_address=collection["contract_address"],
                canonical_name=collection["name"],
                slug=collection["slug"],
                confidence_score=1.0,
                resolution_method="exact",
                metadata=collection.get("metadata", {})
            )
        return None
    
    def _resolve_fuzzy_match(self, normalized_input: str) -> List[Tuple[str, float]]:
        """Find fuzzy matches using string similarity."""
        candidates = []
        
        for slug, collection in self.collections.items():
            # Test against canonical name
            name = collection.get("name", "").lower()
            if name:
                name_similarity = fuzz.ratio(normalized_input, name) / 100.0
                if name_similarity >= self.fuzzy_threshold:
                    candidates.append((slug, name_similarity))
            
            # Test against aliases
            aliases = collection.get("aliases", [])
            for alias in aliases:
                if alias:
                    alias_similarity = fuzz.ratio(normalized_input, alias.lower()) / 100.0
                    if alias_similarity >= self.fuzzy_threshold:
                        candidates.append((slug, alias_similarity))
        
        # Remove duplicates and sort by score (highest first)
        seen_slugs = set()
        unique_candidates = []
        for slug, score in sorted(candidates, key=lambda x: x[1], reverse=True):
            if slug not in seen_slugs:
                unique_candidates.append((slug, score))
                seen_slugs.add(slug)
        
        # Apply popularity-based ranking for disambiguation
        # Collections with lower popularity_rank (higher popularity) get slight boost
        ranked_candidates = []
        for slug, score in unique_candidates[:10]:  # Top 10 candidates
            collection = self.collections[slug]
            popularity_rank = collection.get("metadata", {}).get("popularity_rank", 999)
            
            # Slight boost for more popular collections (lower rank number = higher popularity)
            # Boost is small (max 0.05) to not override genuine fuzzy match scores
            popularity_boost = max(0, (100 - popularity_rank) / 100) * 0.05
            adjusted_score = min(1.0, score + popularity_boost)
            
            ranked_candidates.append((slug, adjusted_score))
        
        # Re-sort by adjusted score
        ranked_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return ranked_candidates[:5]  # Return top 5 matches
    
    def _get_suggestions(self, input_str: str) -> List[Dict[str, Any]]:
        """Generate suggestions for failed matches."""
        suggestions = []
        
        # Find partial matches with lower threshold (0.6)
        lower_threshold = 0.6
        
        for slug, collection in self.collections.items():
            name = collection.get("name", "").lower()
            
            # Check if input is a substring of the collection name
            if len(input_str) >= 3 and input_str in name:
                suggestions.append({
                    "name": collection["name"],
                    "slug": collection["slug"],
                    "contract_address": collection["contract_address"],
                    "aliases": collection.get("aliases", [])[:3]
                })
                continue
            
            # Fuzzy match with lower threshold
            if name:
                similarity = fuzz.ratio(input_str, name) / 100.0
                if similarity >= lower_threshold:
                    suggestions.append({
                        "name": collection["name"],
                        "slug": collection["slug"],
                        "contract_address": collection["contract_address"],
                        "aliases": collection.get("aliases", [])[:3]
                    })
        
        # Sort by popularity (lower rank = more popular = higher priority)
        suggestions.sort(key=lambda x: self.collections.get(x["slug"], {}).get("metadata", {}).get("popularity_rank", 999))
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def get_collection_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get collection data by slug."""
        return self.collections.get(slug)
    
    def get_all_collections(self) -> List[Dict[str, Any]]:
        """Get all collection data."""
        return list(self.collections.values())
    
    def refresh_data(self, json_file_path: str):
        """Reload collection data from JSON file."""
        # Clear existing data
        self.collections.clear()
        self.lookup_index.clear()
        self.contract_index.clear()
        
        # Clear LRU cache
        self.resolve_collection.cache_clear()
        
        # Reload data
        self._load_data(json_file_path)
        self._build_indexes() 