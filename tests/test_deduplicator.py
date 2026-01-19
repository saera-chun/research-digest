"""
Test Deduplicator Module
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.deduplicator import Deduplicator


def test_new_deduplicator():
    """Test creating a new deduplicator with no seen file"""
    test_file = "data/test_seen.json"
    
    # Clean up if exists
    if Path(test_file).exists():
        Path(test_file).unlink()
    
    dedup = Deduplicator(test_file)
    assert len(dedup.seen) == 0, "Should start with empty seen list"
    
    stats = dedup.get_stats()
    assert stats['total'] == 0
    print("✓ New deduplicator works")


def test_filter_new():
    """Test filtering new vs seen articles"""
    test_file = "data/test_seen.json"
    
    # Clean up
    if Path(test_file).exists():
        Path(test_file).unlink()
    
    dedup = Deduplicator(test_file)
    
    articles = [
        {'title': 'Article 1', 'url': 'http://example.com/1', 'doi': '10.1234/abc'},
        {'title': 'Article 2', 'url': 'http://example.com/2', 'doi': '10.1234/def'},
        {'title': 'Article 3', 'url': 'http://example.com/3', 'doi': None},
    ]
    
    # First time - all should be new
    new = dedup.filter_new(articles)
    assert len(new) == 3, "All articles should be new initially"
    
    # Mark as seen
    dedup.mark_as_seen(articles)
    
    # Second time - none should be new
    new = dedup.filter_new(articles)
    assert len(new) == 0, "No articles should be new after marking seen"
    
    # Add one new article
    articles.append({'title': 'Article 4', 'url': 'http://example.com/4', 'doi': '10.1234/ghi'})
    new = dedup.filter_new(articles)
    assert len(new) == 1, "Only new article should be returned"
    assert new[0]['title'] == 'Article 4'
    
    print("✓ Filtering works correctly")
    
    # Clean up
    Path(test_file).unlink()


def test_persistence():
    """Test that seen articles persist across instances"""
    test_file = "data/test_seen.json"
    
    # Clean up
    if Path(test_file).exists():
        Path(test_file).unlink()
    
    # First instance
    dedup1 = Deduplicator(test_file)
    articles = [
        {'title': 'Article 1', 'url': 'http://example.com/1', 'doi': '10.1234/abc'},
    ]
    dedup1.mark_as_seen(articles)
    
    # Second instance (simulates restart)
    dedup2 = Deduplicator(test_file)
    assert len(dedup2.seen) == 1, "Should load previously seen articles"
    
    new = dedup2.filter_new(articles)
    assert len(new) == 0, "Previously seen article should still be filtered"
    
    print("✓ Persistence works")
    
    # Clean up
    Path(test_file).unlink()


def test_article_id_priority():
    """Test that DOI is preferred over URL for identification"""
    test_file = "data/test_seen.json"
    
    # Clean up
    if Path(test_file).exists():
        Path(test_file).unlink()
    
    dedup = Deduplicator(test_file)
    
    # Same article, different URLs, same DOI
    article1 = {'title': 'Article', 'url': 'http://example.com/1', 'doi': '10.1234/abc'}
    article2 = {'title': 'Article', 'url': 'http://different.com/2', 'doi': '10.1234/abc'}
    
    dedup.mark_as_seen([article1])
    
    # Should recognize as duplicate despite different URL
    new = dedup.filter_new([article2])
    assert len(new) == 0, "Should recognize as same article via DOI"
    
    print("✓ DOI-based identification works")
    
    # Clean up
    Path(test_file).unlink()


def test_stats():
    """Test statistics reporting"""
    test_file = "data/test_seen.json"
    
    # Clean up
    if Path(test_file).exists():
        Path(test_file).unlink()
    
    dedup = Deduplicator(test_file)
    
    articles = [
        {'title': 'Article 1', 'url': 'http://example.com/1', 'doi': '10.1234/abc'},
        {'title': 'Article 2', 'url': 'http://example.com/2', 'doi': '10.1234/def'},
        {'title': 'Article 3', 'url': 'http://example.com/3', 'doi': None},
    ]
    
    dedup.mark_as_seen(articles)
    stats = dedup.get_stats()
    
    assert stats['total'] == 3
    assert stats['doi_count'] == 2, "Should have 2 articles tracked by DOI"
    assert stats['url_count'] == 1, "Should have 1 article tracked by URL"
    
    print(f"✓ Stats: {stats}")
    
    # Clean up
    Path(test_file).unlink()


def test_url_to_doi_upgrade():
    """Test that article first seen by URL, then with DOI added, is not duplicated"""
    test_file = "data/test_seen.json"
    
    # Clean up
    if Path(test_file).exists():
        Path(test_file).unlink()
    
    dedup = Deduplicator(test_file)
    
    # Day 1: Article appears without DOI
    article_no_doi = {'title': 'Article', 'url': 'http://example.com/1', 'doi': None}
    dedup.mark_as_seen([article_no_doi])
    
    # Day 2: Same article, now with DOI
    article_with_doi = {'title': 'Article', 'url': 'http://example.com/1', 'doi': '10.1234/abc'}
    new = dedup.filter_new([article_with_doi])
    
    assert len(new) == 0, "Should recognize as duplicate via URL even though DOI is now present"
    
    print("✓ URL→DOI upgrade prevention works")
    
    # Clean up
    Path(test_file).unlink()


if __name__ == "__main__":
    print("Running Deduplicator Tests...\n")
    print("="*60)
    
    test_new_deduplicator()
    print("✓ test_new_deduplicator passed")
    
    test_filter_new()
    print("✓ test_filter_new passed")
    
    test_persistence()
    print("✓ test_persistence passed")
    
    test_article_id_priority()
    print("✓ test_article_id_priority passed")
    
    test_stats()
    print("✓ test_stats passed")
    
    test_url_to_doi_upgrade()
    print("✓ test_url_to_doi_upgrade passed")
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
