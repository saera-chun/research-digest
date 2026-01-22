"""
Metadata Fetcher Module

Fetches detailed article metadata (abstracts, authors, keywords) from academic APIs.
Uses caching to avoid redundant API calls.
"""

import requests
import logging
import json
import time
from pathlib import Path
from typing import Dict, Optional, List
from src.analysers.metadata_extractor import extract_all
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MetadataFetcher:
    """Fetches article metadata from Crossref and OpenAlex APIs"""
    
    def __init__(self, cache_file: str = "data/doi_cache.json", 
                 contact_email: str = "your-email@example.com"):
        """
        Initialize metadata fetcher with cache and API configuration
        
        Args:
            cache_file: Path to JSON file for caching API responses
            contact_email: Email for Crossref polite pool (faster rate limits)
        """
        self.cache_file = Path(cache_file)
        self.contact_email = contact_email
        self.cache = self._load_cache()
        
        # API endpoints
        self.crossref_base = "https://api.crossref.org/works/"
        self.openalex_base = "https://api.openalex.org/works/"
        
        # Rate limiting (50 req/sec for Crossref polite pool, but we'll be conservative)
        self.min_request_interval = 0.1  # 100ms between requests = 10 req/sec
        self.last_request_time = 0
    
    def _load_cache(self) -> Dict:
        """Load cached metadata from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                logger.info(f"Loaded {len(cache)} cached entries")
                return cache
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save metadata cache to file"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _rate_limit(self):
        """Enforce rate limiting between API requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def fetch_metadata(self, article: Dict) -> Dict:
        """
        Fetch metadata for an article (abstract, authors, keywords)
        
        Args:
            article: Dict with 'doi' and/or 'url' fields from RSS fetcher
            
        Returns:
            Enhanced article dict with additional metadata fields:
                - title: str (overrides RSS title with canonical API title)
                - abstract: str or None
                - authors: List[str]
                - keywords: List[str]
                - publication_date: str (ISO format)
                - journal: str (clean journal name from API)
        """
        doi = article.get('doi')

        # Check cache first
        if doi and doi in self.cache:
            cached = self.cache[doi]
            # Cache expires after 30 days (in case metadata gets updated)
            cache_date = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
            if datetime.now() - cache_date < timedelta(days=30):
                logger.debug(f"Cache hit: {doi}")
                merged = {**article, **cached['metadata']}
                # Ensure extracted fields exist; if not, extract and persist to cache
                if not any(k in merged for k in ('geography', 'methods', 'stakeholders')):
                    extracted = extract_all(merged)
                    merged.update(extracted)
                    # update cache metadata to include extracted fields
                    try:
                        self.cache[doi]['metadata'].update(extracted)
                        self._save_cache()
                    except Exception:
                        pass
                return merged

        # Try fetching from APIs
        metadata = None

        if doi:
            # Try Crossref first
            metadata = self._fetch_from_crossref(doi)

            # Fallback to OpenAlex if Crossref fails or has no abstract
            if not metadata or not metadata.get('abstract'):
                metadata = self._fetch_from_openalex(doi)

        # If we got metadata, merge and extract
        if metadata:
            merged = {**article, **metadata}
            extracted = extract_all(merged)
            merged.update(extracted)

            if doi:
                # Store merged metadata including extracted fields in cache
                try:
                    self.cache[doi] = {
                        'cached_at': datetime.now().isoformat(),
                        'metadata': merged
                    }
                    self._save_cache()
                except Exception:
                    logger.debug("Failed to save extracted fields to cache")

            return merged

        # No metadata found, return article with fallback abstract and extracted fields
        logger.warning(f"No metadata found for: {article.get('title', 'Unknown')[:50]}")
        fallback_abstract = self._extract_abstract_from_rss_summary(article.get('summary'))
        result = {
            **article,
            'abstract': fallback_abstract,
            'authors': [],
            'keywords': [],
        }
        extracted = extract_all(result)
        result.update(extracted)
        return result
    
    def _fetch_from_crossref(self, doi: str) -> Optional[Dict]:
        """Fetch metadata from Crossref API"""
        try:
            self._rate_limit()
            
            url = f"{self.crossref_base}{doi}"
            headers = {'User-Agent': f'ResearchDigest/0.1 (mailto:{self.contact_email})'}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()['message']
                
                # Extract metadata
                metadata = {
                    'title': data.get('title', [None])[0],  # Crossref returns title as array
                    'abstract': self._clean_abstract(data.get('abstract')),
                    'authors': self._extract_authors(data.get('author', [])),
                    'keywords': data.get('subject', []),  # Some Crossref records have keywords in 'subject'
                    'journal': data.get('container-title', [None])[0],
                }
                
                if 'published' in data or 'published-print' in data:
                    date_parts = data.get('published', data.get('published-print', {})).get('date-parts', [[]])[0]
                    if date_parts:
                        metadata['publication_date'] = self._format_date(date_parts)
                
                logger.debug(f"Crossref: {doi}")
                return metadata
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Crossref API error for {doi}: {e}")
        except Exception as e:
            logger.error(f"Error parsing Crossref data for {doi}: {e}")
        
        return None
    
    def _fetch_from_openalex(self, doi: str) -> Optional[Dict]:
        """Fetch metadata from OpenAlex API"""
        try:
            self._rate_limit()
            
            # OpenAlex expects DOI with https://doi.org/ prefix
            url = f"{self.openalex_base}https://doi.org/{doi}"
            headers = {'User-Agent': f'ResearchDigest/0.1 (mailto:{self.contact_email})'}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract metadata
                metadata = {
                    'title': data.get('title'),  # OpenAlex returns title as string
                    'abstract': self._clean_abstract(data.get('abstract')),
                    'authors': [author['author']['display_name'] for author in data.get('authorships', [])],
                    'keywords': [kw['display_name'] for kw in data.get('keywords', [])],
                    'journal': data.get('primary_location', {}).get('source', {}).get('display_name'),
                }
                
                # Extract publication date
                if data.get('publication_date'):
                    metadata['publication_date'] = data['publication_date']
                
                logger.debug(f"OpenAlex: {doi}")
                return metadata
                
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAlex API error for {doi}: {e}")
        except Exception as e:
            logger.error(f"Error parsing OpenAlex data for {doi}: {e}")
        
        return None
    
    def _clean_abstract(self, abstract: Optional[str]) -> Optional[str]:
        """Clean abstract text (remove HTML tags, extra whitespace)"""
        if not abstract:
            return None
        
        # Remove common XML/HTML tags
        import re
        abstract = re.sub(r'<[^>]+>', '', abstract)
        
        # Remove common prefixes
        prefixes = ['Abstract', 'ABSTRACT', 'Summary', 'SUMMARY']
        for prefix in prefixes:
            if abstract.startswith(prefix):
                abstract = abstract[len(prefix):].lstrip(':').strip()
        
        # Normalize whitespace
        abstract = ' '.join(abstract.split())
        
        return abstract if abstract else None
    
    def _extract_abstract_from_rss_summary(self, summary: Optional[str]) -> Optional[str]:
        """Extract abstract text from RSS summary field (often contains partial abstracts)"""
        if not summary or len(summary) < 50:
            return None
        
        # Clean HTML and extract meaningful text
        cleaned = self._clean_abstract(summary)
        
        if not cleaned:
            return None
        
        # Filter out non-abstract content (volume/issue info, publication dates, etc.)
        # Look for sentences that seem like abstract content (longer, substantive text)
        if len(cleaned) > 100 and not cleaned.startswith('Volume ') and not cleaned.startswith('Publication date'):
            return cleaned
        
        return None
    
    def _extract_authors(self, author_list: List[Dict]) -> List[str]:
        """Extract author names from Crossref author data"""
        authors = []
        for author in author_list:
            # Crossref format: {"given": "John", "family": "Doe"}
            given = author.get('given', '')
            family = author.get('family', '')
            if family:
                name = f"{given} {family}".strip()
                authors.append(name)
        return authors
    
    def _format_date(self, date_parts: List[int]) -> str:
        """Convert date parts [year, month, day] to ISO format"""
        if len(date_parts) == 1:
            return f"{date_parts[0]:04d}"
        elif len(date_parts) == 2:
            return f"{date_parts[0]:04d}-{date_parts[1]:02d}"
        elif len(date_parts) >= 3:
            return f"{date_parts[0]:04d}-{date_parts[1]:02d}-{date_parts[2]:02d}"
        return ""
    
    def fetch_batch(self, articles: List[Dict]) -> List[Dict]:
        """
        Fetch metadata for a batch of articles
        
        Args:
            articles: List of article dicts from RSS fetcher
            
        Returns:
            List of enhanced article dicts with metadata
        """
        enriched = []
        total = len(articles)
        
        for i, article in enumerate(articles, 1):
            print(f"Fetching metadata {i}/{total}: {article.get('title', 'Unknown')[:50]}...")
            enriched_article = self.fetch_metadata(article)
            enriched.append(enriched_article)
        
        print(f"\nEnriched {len(enriched)} articles with metadata")
        return enriched
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the metadata cache"""
        return {
            'total_cached': len(self.cache),
            'cache_file': str(self.cache_file),
            'cache_size_kb': self.cache_file.stat().st_size / 1024 if self.cache_file.exists() else 0
        }
