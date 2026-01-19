"""
Deduplication Module

Tracks seen articles to prevent showing duplicates in daily digests.
Uses seen.json to store article identifiers permanently.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

logger = logging.getLogger(__name__)


class Deduplicator:
    """Manages tracking of seen articles"""
    
    def __init__(self, seen_file: str = "data/seen.json"):
        """Initialize deduplicator with path to seen.json file"""
        self.seen_file = Path(seen_file)
        self.seen = self._load_seen()
    
    def _load_seen(self) -> Dict[str, str]:
        """Load seen articles from JSON file
        
        Returns:
            Dictionary mapping article_id -> date_first_seen
        """
        if not self.seen_file.exists():
            logger.info(f"Seen file not found, starting fresh: {self.seen_file}")
            return {}
        
        try:
            with open(self.seen_file, 'r') as f:
                seen = json.load(f)
            logger.info(f"Loaded {len(seen)} seen articles")
            return seen
        except json.JSONDecodeError:
            logger.error(f"Corrupted seen file, starting fresh: {self.seen_file}")
            return {}
    
    def _save_seen(self):
        """Save seen articles to JSON file"""
        # Create data directory if it doesn't exist
        self.seen_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.seen_file, 'w') as f:
            json.dump(self.seen, f, indent=2)
        logger.info(f"Saved {len(self.seen)} seen articles")
    
    def _get_article_id(self, article: Dict) -> str:
        """Get unique identifier for an article
        
        Priority:
        1. DOI (most reliable)
        2. URL (fallback)
        
        Args:
            article: Article dictionary with 'doi' and 'url' fields
        
        Returns:
            Unique identifier string
        """
        if article.get('doi'):
            return f"doi:{article['doi']}"
        return f"url:{article['url']}"
    
    def filter_new(self, articles: List[Dict]) -> List[Dict]:
        """Filter out articles that have been seen before
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            List of only new (unseen) articles
        """
        new_articles = []
        
        for article in articles:
            # Check both DOI and URL to prevent duplicates
            # (an article might first appear without DOI, then with DOI later)
            doi_id = f"doi:{article['doi']}" if article.get('doi') else None
            url_id = f"url:{article['url']}"
            
            # Skip if we've seen this article by either DOI or URL
            if doi_id and doi_id in self.seen:
                continue  # Seen by DOI
            if url_id in self.seen:
                continue  # Seen by URL
            
            new_articles.append(article)
        
        logger.info(f"Filtered {len(articles)} articles → {len(new_articles)} new")
        return new_articles
    
    def mark_as_seen(self, articles: List[Dict]):
        """Mark articles as seen with current timestamp
        
        Args:
            articles: List of article dictionaries to mark as seen
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        for article in articles:
            article_id = self._get_article_id(article)
            if article_id not in self.seen:
                self.seen[article_id] = today
        
        self._save_seen()
        logger.info(f"Marked {len(articles)} articles as seen")
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about seen articles
        
        Returns:
            Dictionary with 'total', 'doi_count', 'url_count'
        """
        doi_count = sum(1 for k in self.seen.keys() if k.startswith('doi:'))
        url_count = sum(1 for k in self.seen.keys() if k.startswith('url:'))
        
        return {
            'total': len(self.seen),
            'doi_count': doi_count,
            'url_count': url_count,
        }
