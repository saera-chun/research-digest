#!/usr/bin/env python3
"""
Test script for the complete pipeline so far:
RSS Fetcher → Deduplicator → Metadata Fetcher

Usage:
    python test_pipeline.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from collectors.rss_fetcher import RSSFetcher
from utils.deduplicator import Deduplicator
from collectors.metadata_fetcher import MetadataFetcher


def main():
    print("=" * 70)
    print("RESEARCH DIGEST - PIPELINE TEST")
    print("=" * 70)
    print()
    
    # Step 1: Fetch articles from RSS feeds
    print("Step 1: Fetching articles from RSS feeds...")
    print("-" * 70)
    fetcher = RSSFetcher('feeds.example.txt')
    articles = fetcher.fetch_all()
    print(f"✓ Fetched {len(articles)} articles from {len(fetcher.feeds)} feeds")
    print()
    
    # Step 2: Filter out already seen articles
    print("Step 2: Filtering out seen articles...")
    print("-" * 70)
    dedup = Deduplicator('data/seen.json')
    stats_before = dedup.get_stats()
    print(f"  Previously seen: {stats_before['total']} articles")
    print(f"    - {stats_before['doi_count']} with DOIs")
    print(f"    - {stats_before['url_count']} URL-only")
    
    new_articles = dedup.filter_new(articles)
    print(f"✓ Found {len(new_articles)} new articles")
    print()
    
    # Step 3: Enrich with metadata
    if new_articles:
        print("Step 3: Enriching with metadata...")
        print("-" * 70)
        metadata_fetcher = MetadataFetcher('data/doi_cache.json')
        
        # Test with first 10 articles to ensure we hit some with DOIs
        sample_articles = new_articles[:10]
        print(f"  Testing with first {len(sample_articles)} articles:")
        print()
        
        enriched = metadata_fetcher.fetch_batch(sample_articles)
        
        for i, article in enumerate(enriched, 1):
            print(f"  Article {i}:")
            print(f"    Title (RSS):  {article.get('title', 'N/A')[:60]}...")
            
            # Check if metadata was enriched (fields added at top level, not nested)
            has_metadata = any([
                article.get('authors'),
                article.get('keywords'),
                article.get('journal'),
                article.get('abstract'),
                article.get('publication_date')
            ])
            
            if has_metadata:
                authors = article.get('authors', [])
                if authors:
                    print(f"    Authors:      {', '.join(authors[:3])}")
                
                keywords = article.get('keywords', [])
                if keywords:
                    print(f"    Keywords:     {', '.join(keywords[:5])}")
                
                journal = article.get('journal')
                if journal:
                    print(f"    Journal:      {journal}")
                
                pub_date = article.get('publication_date')
                if pub_date:
                    print(f"    Pub Date:     {pub_date}")
                
                abstract = article.get('abstract', '')
                if abstract:
                    abstract_preview = abstract[:100].replace('\n', ' ')
                    print(f"    Abstract:     {abstract_preview}...")
            else:
                print(f"    Metadata:     Not available")
            
            print()
        
        print(f"✓ Enriched {len(enriched)} articles with metadata")
        print()
        
        # Show cache stats
        cache_stats = metadata_fetcher.get_cache_stats()
        print("  Cache statistics:")
        print(f"    Total cached: {cache_stats['total_cached']}")
        print(f"    Cache file: {cache_stats['cache_file']}")
        print(f"    Cache size: {cache_stats['cache_size_kb']:.1f} KB")
        print()
    else:
        print("Step 3: Skipped (no new articles)")
        print()
    
    # Summary
    print("=" * 70)
    print("PIPELINE TEST SUMMARY")
    print("=" * 70)
    print(f"Total fetched:     {len(articles)}")
    print(f"Already seen:      {len(articles) - len(new_articles)}")
    print(f"New articles:      {len(new_articles)}")
    print(f"Sample enriched:   {min(10, len(new_articles))}")
    print()
    
    if new_articles:
        print("Next steps:")
        print("  - Implement Article Ranker (keyword scoring)")
        print("  - Implement Metadata Extractor (geography, methods, stakeholders)")
        print("  - Implement Obsidian Writer (create notes)")
        print("  - Implement Email Handler (send digest)")
    else:
        print("All articles have been seen before!")
        print("To test with fresh data, you could:")
        print("  1. Clear data/seen.json (backup first!)")
        print("  2. Add new RSS feeds to feeds.example.txt")
    print()


if __name__ == '__main__':
    main()
