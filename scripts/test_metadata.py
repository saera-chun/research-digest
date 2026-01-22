#!/usr/bin/env python3
"""
Test metadata fetcher with real DOIs from seen.json
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.metadata_fetcher import MetadataFetcher


def main():
    # Load some DOIs from seen.json
    seen_file = Path("data/seen.json")
    
    if not seen_file.exists():
        print("Error: data/seen.json not found")
        return
    
    with open(seen_file, 'r') as f:
        seen = json.load(f)
    
    # Extract DOIs (they have format "doi:10.xxxx/...")
    dois = [key.replace('doi:', '') for key in seen.keys() if key.startswith('doi:')]
    
    print(f"Found {len(dois)} DOIs in seen.json")
    print(f"Testing with first 3 DOIs...\n")
    
    # Test with first 3 DOIs
    test_dois = dois[:3]
    
    # Create metadata fetcher
    fetcher = MetadataFetcher(contact_email="your-email@example.com")
    
    for i, doi in enumerate(test_dois, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}/3: {doi}")
        print('='*70)
        
        # Create article dict (minimal format from RSS)
        article = {
            'title': 'Test Article',
            'url': f'https://doi.org/{doi}',
            'doi': doi
        }
        
        # Fetch metadata
        enriched = fetcher.fetch_metadata(article)
        
        # Display results
        print(f"\nTitle: {enriched.get('title', 'N/A')}")
        print(f"DOI: {enriched.get('doi', 'N/A')}")
        print(f"\nJournal: {enriched.get('journal', 'N/A')}")
        print(f"Publication Date: {enriched.get('publication_date', 'N/A')}")
        
        print(f"\nAuthors ({len(enriched.get('authors', []))} total):")
        for author in enriched.get('authors', [])[:5]:  # Show first 5
            print(f"  - {author}")
        if len(enriched.get('authors', [])) > 5:
            print(f"  ... and {len(enriched['authors']) - 5} more")
        
        print(f"\nKeywords ({len(enriched.get('keywords', []))} total):")
        for keyword in enriched.get('keywords', [])[:10]:  # Show first 10
            print(f"  - {keyword}")
        if len(enriched.get('keywords', [])) > 10:
            print(f"  ... and {len(enriched['keywords']) - 10} more")
        
        abstract = enriched.get('abstract')
        if abstract:
            print(f"\nAbstract ({len(abstract)} chars):")
            print(f"  {abstract[:200]}...")
        else:
            print("\nAbstract: Not available")
    
    # Show cache stats
    print(f"\n{'='*70}")
    print("CACHE STATISTICS")
    print('='*70)
    stats = fetcher.get_cache_stats()
    print(f"Total cached entries: {stats['total_cached']}")
    print(f"Cache file: {stats['cache_file']}")
    print(f"Cache size: {stats['cache_size_kb']:.2f} KB")


if __name__ == '__main__':
    main()
