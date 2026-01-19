"""
Test RSS Fetcher Module
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.rss_fetcher import RSSFetcher


def test_load_feeds():
    """Test that feeds are loaded from file"""
    fetcher = RSSFetcher("feeds.example.txt")
    assert len(fetcher.feeds) > 0, "Should load at least one feed"
    assert all(isinstance(feed, str) for feed in fetcher.feeds), "All feeds should be strings"


def test_fetch_all():
    """Test fetching articles from all feeds"""
    fetcher = RSSFetcher("feeds.example.txt")
    articles = fetcher.fetch_all()
    
    assert len(articles) > 0, "Should fetch at least some articles"
    
    # Check first article structure
    first = articles[0]
    assert 'title' in first, "Article should have title"
    assert 'url' in first, "Article should have url"
    assert 'doi' in first, "Article should have doi field"
    assert 'published_date' in first, "Article should have published_date"
    assert 'feed_title' in first, "Article should have feed_title"
    assert 'feed_url' in first, "Article should have feed_url"
    
    # Check values are populated
    assert first['title'], "Title should not be empty"
    assert first['url'], "URL should not be empty"
    assert first['feed_title'], "Feed title should not be empty"
    assert first['feed_url'], "Feed URL should not be empty"
    
    print(f"\n✓ Fetched {len(articles)} total articles")
    print(f"✓ Sample article: {first['title'][:60]}...")
    print(f"✓ Journal: {first['feed_title']}")
    print(f"✓ DOI: {first['doi']}")


def test_fetch_single_feed():
    """Test fetching from a single feed"""
    fetcher = RSSFetcher("feeds.example.txt")
    
    # Get first feed URL
    feed_url = fetcher.feeds[0]
    articles = fetcher._fetch_feed(feed_url)
    
    assert isinstance(articles, list), "Should return a list"
    
    if articles:  # Some feeds might be empty
        assert 'title' in articles[0], "Article should have required fields"
        print(f"\n✓ Single feed test: got {len(articles)} articles from first feed")


def test_clean_feed_title():
    """Test RSS title cleaning"""
    fetcher = RSSFetcher("feeds.example.txt")
    
    # Test publisher prefix removal
    assert fetcher._clean_feed_title("tandf: Housing Studies: Table of Contents") == "Housing Studies"
    assert fetcher._clean_feed_title("SAGE Publications Ltd: Urban Studies") == "Urban Studies"
    
    # Test suffix removal
    assert fetcher._clean_feed_title("Journal Name: Table of Contents") == "Journal Name"
    assert fetcher._clean_feed_title("Journal Name: TOC") == "Journal Name"
    
    print("\n✓ Title cleaning works correctly")


if __name__ == "__main__":
    # Run tests manually
    print("Running RSS Fetcher Tests...\n")
    print("="*60)
    
    test_load_feeds()
    print("✓ test_load_feeds passed")
    
    test_fetch_all()
    print("✓ test_fetch_all passed")
    
    test_fetch_single_feed()
    print("✓ test_fetch_single_feed passed")
    
    test_clean_feed_title()
    print("✓ test_clean_feed_title passed")
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
