#!/usr/bin/env python3
"""
Test Article Ranker with real pipeline data
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from collectors.rss_fetcher import RSSFetcher
from utils.deduplicator import Deduplicator
from collectors.metadata_fetcher import MetadataFetcher
from analysers.article_ranker import ArticleRanker


# Sample boost keywords for testing
BOOST_KEYWORDS = {
    "housing": 40,
    "policy": 35,
    "tenure": 30,
    "affordability": 30,
    "spatial": 25,
    "qualitative": 20,
    "auckland": 20,
    "precarity": 20,
}


def main():
    print("=" * 70)
    print("ARTICLE RANKER TEST WITH REAL DATA")
    print("=" * 70)
    print()
    
    # Fetch and enrich articles
    print("Fetching articles...")
    fetcher = RSSFetcher('feeds.example.txt')
    articles = fetcher.fetch_all()
    
    dedup = Deduplicator('data/seen.json')
    new_articles = dedup.filter_new(articles)
    print(f"Found {len(new_articles)} new articles")
    print()
    
    # Enrich sample
    print("Enriching first 20 articles...")
    metadata_fetcher = MetadataFetcher('data/doi_cache.json')
    enriched = metadata_fetcher.fetch_batch(new_articles[:20])
    print(f"Enriched {len(enriched)} articles")
    print()
    
    # Rank articles
    print("Ranking articles...")
    print("-" * 70)
    ranker = ArticleRanker(BOOST_KEYWORDS)
    ranked = ranker.rank_articles(enriched)
    
    # Show statistics
    stats = ranker.get_statistics(ranked)
    print(f"\nRanking Statistics:")
    print(f"  Total articles:  {stats['total_articles']}")
    print(f"  Score range:     {stats['min']} - {stats['max']}")
    print(f"  Mean score:      {stats['mean']:.1f}")
    print(f"  Median score:    {stats['median']:.1f}")
    print(f"  Zero scores:     {stats['zero_score']}")
    print()
    
    # Show top 10
    print("=" * 70)
    print("TOP 10 RANKED ARTICLES")
    print("=" * 70)
    
    for i, article in enumerate(ranked[:10], 1):
        print(f"\n{i}. SCORE: {article['score']}")
        print(f"   Title: {article['title'][:65]}...")
        print(f"   Journal: {article.get('journal', 'N/A')}")
        
        keywords = article.get('keywords', [])
        if keywords:
            print(f"   Keywords: {', '.join(keywords[:4])}")
    
    print()
    print("=" * 70)
    print(f"Ranker successfully ranked {len(ranked)} articles!")
    print()


if __name__ == '__main__':
    main()
