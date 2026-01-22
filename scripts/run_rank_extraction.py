#!/usr/bin/env python3
"""
Run a short pipeline to fetch real RSS feeds, enrich a sample of new articles,
and print extracted metadata (geography, methods, stakeholders) and ranking info.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.rss_fetcher import RSSFetcher
from src.utils.deduplicator import Deduplicator
from src.collectors.metadata_fetcher import MetadataFetcher
from src.analysers.article_ranker import ArticleRanker


BOOST = {
    "housing-policy": 40,
    "phenomenology": 60,
    "auckland": 15,
}


def main():
    print("Fetching articles...")
    fetcher = RSSFetcher('feeds.example.txt')
    articles = fetcher.fetch_all()

    dedup = Deduplicator('data/seen.json')
    new_articles = dedup.filter_new(articles)
    print(f"Found {len(new_articles)} new articles")

    # Enrich first 20
    metadata_fetcher = MetadataFetcher('data/doi_cache.json')
    sample = new_articles[:20]
    enriched = metadata_fetcher.fetch_batch(sample)

    print('\nEnriched sample outputs:')
    for i, art in enumerate(enriched, 1):
        print(f"\n{i}. {art.get('title')[:80]}")
        print(f"   Journal: {art.get('journal')}")
        print(f"   DOI: {art.get('doi')}")
        print(f"   Keywords: {art.get('keywords')}")
        print(f"   Geography: {art.get('geography')}")
        print(f"   Methods: {art.get('methods')}")
        print(f"   Stakeholders: {art.get('stakeholders')}")

    # Rank
    ranker = ArticleRanker(BOOST)
    ranked = ranker.rank_articles(enriched)

    print('\nTop 10 by score:')
    for a in ranked[:10]:
        print(f"SCORE: {a['score']:3d}  Title: {a.get('title')[:60]}")
        print(f"   Geo: {a.get('geography')}, Methods: {a.get('methods')}, Stakeholders: {a.get('stakeholders')}")


if __name__ == '__main__':
    main()
