#!/usr/bin/env python3
"""
Example usage of the NFT Collection Resolver.

This script demonstrates how to use the NFT collection resolver to:
1. Resolve exact collection names
2. Handle typos and fuzzy matching
3. Resolve contract addresses
4. Handle ambiguous queries
5. Get suggestions for failed matches
"""

import json
from collection_resolver import NFTCollectionResolver, CollectionResolutionResult


def print_result(result: CollectionResolutionResult, query: str):
    """Pretty print a resolution result."""
    print(f"\n--- Query: '{query}' ---")
    
    if result.success:
        print(f"✅ SUCCESS ({result.resolution_method})")
        print(f"   Collection: {result.canonical_name}")
        print(f"   Contract: {result.contract_address}")
        print(f"   Slug: {result.slug}")
        print(f"   Confidence: {result.confidence_score:.2f}")
        if result.metadata:
            print(f"   Popularity Rank: {result.metadata.get('popularity_rank', 'N/A')}")
    else:
        print(f"❌ FAILED: {result.error_message}")
        
        if result.error_message == "AMBIGUOUS" and result.alternatives:
            print("   Disambiguation options:")
            for i, alt in enumerate(result.alternatives, 1):
                print(f"   {i}. {alt['name']} ({alt['contract_address']})")
                if alt.get('aliases'):
                    print(f"      Aliases: {', '.join(alt['aliases'][:3])}")
        
        elif result.alternatives:
            print("   Suggestions:")
            for i, alt in enumerate(result.alternatives, 1):
                print(f"   {i}. {alt['name']}")


def main():
    """Demonstrate the NFT collection resolver functionality."""
    print("🔍 NFT Collection Resolver - Example Usage")
    print("=" * 50)
    
    # Initialize the resolver
    try:
        resolver = NFTCollectionResolver("collections.json")
        print(f"✅ Loaded {len(resolver.get_all_collections())} collections")
    except Exception as e:
        print(f"❌ Failed to load resolver: {e}")
        return
    
    # Test cases demonstrating different functionality
    test_cases = [
        # Exact matches
        "CryptoPunks",
        "Bored Ape Yacht Club",
        
        # Aliases
        "BAYC",
        "MAYC", 
        "punks",
        "wpunks",
        
        # Contract addresses
        "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb",  # CryptoPunks
        "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",  # BAYC
        
        # Case insensitive
        "bayc",
        "CRYPTOPUNKS",
        
        # Fuzzy matching (typos)
        "Bored Ape Yatch Club",  # "Yacht" typo
        "CryptoPunkz",           # Wrong letter
        "azukii",                # Extra letter
        
        # Potential ambiguity
        "apes",
        
        # Partial matches
        "Bored",
        "Crypto",
        
        # Should fail
        "xyz123",
        "random text",
        
        # Invalid input
        "",
        "a" * 101,  # Too long
    ]
    
    print("\n🧪 Running test cases...")
    print("-" * 30)
    
    for query in test_cases:
        try:
            result = resolver.resolve_collection(query)
            print_result(result, query)
        except Exception as e:
            print(f"\n--- Query: '{query}' ---")
            print(f"💥 EXCEPTION: {e}")
    
    # Demonstrate additional functionality
    print("\n\n📊 Additional Features")
    print("-" * 30)
    
    # Get collection by slug
    collection = resolver.get_collection_by_slug("cryptopunks")
    if collection:
        print(f"✅ Retrieved collection by slug: {collection['name']}")
    
    # List all collections
    all_collections = resolver.get_all_collections()
    print(f"✅ Total collections in database: {len(all_collections)}")
    
    # Show some popular collections
    popular_collections = sorted(
        [c for c in all_collections if c.get('metadata', {}).get('popularity_rank')],
        key=lambda x: x['metadata']['popularity_rank']
    )[:5]
    
    print("\n🏆 Top 5 Most Popular Collections:")
    for i, collection in enumerate(popular_collections, 1):
        print(f"   {i}. {collection['name']} (rank {collection['metadata']['popularity_rank']})")
    
    print("\n✨ Example completed successfully!")


if __name__ == "__main__":
    main() 