"""
RSS Feed Fetcher Module

Fetches articles from RSS feeds and extracts basic metadata.
"""

import feedparser
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class RSSFetcher:
    """Fetches and parses RSS feeds from academic journals"""
    
    def __init__(self, feeds_file: str = "feeds.txt"):
        """Initialize RSS fetcher with path to feeds file"""
        self.feeds_file = feeds_file
        self.feeds = self._load_feeds()
    
    def _load_feeds(self) -> List[str]:
        """Load RSS feed URLs from file, skip comments and empty lines"""
        feeds = []
        try:
            with open(self.feeds_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        # Remove inline comments
                        feed_url = line.split('#')[0].strip()
                        if feed_url:
                            feeds.append(feed_url)
            logger.info(f"Loaded {len(feeds)} RSS feeds")
        except FileNotFoundError:
            logger.error(f"Feeds file not found: {self.feeds_file}")
        return feeds
    
    def fetch_all(self) -> List[Dict]:
        """Fetch articles from all RSS feeds"""
        all_articles = []
        
        for feed_url in self.feeds:
            print(f"Fetching: {feed_url}")
            articles = self._fetch_feed(feed_url)
            all_articles.extend(articles)
            print(f"  → Got {len(articles)} articles")
        
        print(f"\nTotal: {len(all_articles)} articles")
        return all_articles
    
    def _fetch_feed(self, feed_url: str) -> List[Dict]:
        """Fetch and parse a single RSS feed"""
        articles = []
        
        try:
            feed = feedparser.parse(feed_url)
            feed_title = self._clean_feed_title(feed.feed.get('title', 'Unknown'))
            
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', '').strip(),
                    'url': entry.get('link', ''),
                    'doi': self._extract_doi(entry),
                    'published_date': entry.get('published', ''),
                    'feed_title': feed_title,
                    'feed_url': feed_url,
                    'summary': entry.get('summary', '').strip(),  # RSS summary (may contain partial abstract)
                }
                
                if article['title'] and article['url']:
                    articles.append(article)
                    
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        return articles
    
    def _clean_feed_title(self, title: str) -> str:
        """Clean RSS feed title by removing publisher prefixes/suffixes
        
        Note: This is a temporary solution using regex patterns.
        Later, it will be replaced with clean journal names from DOI metadata
        (Crossref/OpenAlex APIs provide standardized journal titles).
        """
        # Remove common publisher prefixes
        prefixes = [
            r'^tandf:\s*',
            r'^SAGE Publications Ltd:\s*',
            r'^SAGE Publications:\s*',
            r'^ScienceDirect Publication:\s*',
        ]
        for pattern in prefixes:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Remove common table of contents suffixes
        suffixes = [
            r':\s*Table of Contents$',
            r':\s*Table Of Contents$',
            r':\s*TOC$',
        ]
        for pattern in suffixes:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        return title.strip()
    
    def _extract_doi(self, entry) -> Optional[str]:
        """Extract DOI from RSS entry"""
        # Method 1: Direct DOI field
        if hasattr(entry, 'prism_doi'):
            return entry.prism_doi
        
        # Method 2: Parse from link
        link = entry.get('link', '')
        doi_match = re.search(r'10\.\d{4,}/[^\s]+', link)
        if doi_match:
            return doi_match.group(0)
        
        return None