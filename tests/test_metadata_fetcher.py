"""
Tests for metadata fetcher module
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
from src.collectors.metadata_fetcher import MetadataFetcher


@pytest.fixture
def temp_cache(tmp_path):
    """Create temporary cache file for testing"""
    cache_file = tmp_path / "test_cache.json"
    return str(cache_file)


@pytest.fixture
def fetcher(temp_cache):
    """Create metadata fetcher instance with temp cache"""
    return MetadataFetcher(cache_file=temp_cache, contact_email="test@example.com")


@pytest.fixture
def sample_article():
    """Sample article from RSS fetcher"""
    return {
        'title': 'Housing Policy and Urban Development',
        'url': 'https://example.com/article/123',
        'doi': '10.1234/example.123',
        'published_date': '2026-01-15',
        'feed_title': 'Housing Studies',
        'feed_url': 'https://example.com/rss'
    }


def test_fetcher_initialization(fetcher, temp_cache):
    """Test metadata fetcher initializes correctly"""
    assert fetcher.cache_file == Path(temp_cache)
    assert fetcher.contact_email == "test@example.com"
    assert isinstance(fetcher.cache, dict)
    assert len(fetcher.cache) == 0


def test_cache_persistence(fetcher, sample_article):
    """Test that cache is saved and loaded correctly"""
    # Add metadata to cache
    doi = sample_article['doi']
    fetcher.cache[doi] = {
        'cached_at': '2026-01-22T10:00:00',
        'metadata': {
            'abstract': 'Test abstract',
            'authors': ['John Doe'],
            'keywords': ['housing', 'policy']
        }
    }
    fetcher._save_cache()
    
    # Create new fetcher instance (should load from cache)
    new_fetcher = MetadataFetcher(cache_file=str(fetcher.cache_file))
    assert doi in new_fetcher.cache
    assert new_fetcher.cache[doi]['metadata']['abstract'] == 'Test abstract'


def test_fetch_metadata_from_cache(fetcher, sample_article):
    """Test fetching metadata from cache"""
    doi = sample_article['doi']
    
    # Pre-populate cache
    from datetime import datetime
    fetcher.cache[doi] = {
        'cached_at': datetime.now().isoformat(),
        'metadata': {
            'abstract': 'Cached abstract',
            'authors': ['Jane Smith'],
            'keywords': ['urban', 'development'],
            'journal': 'Housing Studies'
        }
    }
    
    # Fetch should return cached data without API call
    with patch.object(fetcher, '_fetch_from_crossref') as mock_crossref:
        result = fetcher.fetch_metadata(sample_article)
        
        # Should not call API
        mock_crossref.assert_not_called()
        
        # Should have cached metadata
        assert result['abstract'] == 'Cached abstract'
        assert result['authors'] == ['Jane Smith']
        assert result['keywords'] == ['urban', 'development']


@patch('requests.get')
def test_fetch_from_crossref(mock_get, fetcher, sample_article):
    """Test fetching metadata from Crossref API"""
    # Mock Crossref API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'message': {
            'abstract': '<p>This is a test abstract about housing policy.</p>',
            'author': [
                {'given': 'John', 'family': 'Doe'},
                {'given': 'Jane', 'family': 'Smith'}
            ],
            'subject': ['Housing', 'Urban Policy'],
            'container-title': ['Housing Studies'],
            'published': {'date-parts': [[2026, 1, 15]]}
        }
    }
    mock_get.return_value = mock_response
    
    metadata = fetcher._fetch_from_crossref(sample_article['doi'])
    
    assert metadata is not None
    assert 'This is a test abstract' in metadata['abstract']
    assert len(metadata['authors']) == 2
    assert 'John Doe' in metadata['authors']
    assert metadata['keywords'] == ['Housing', 'Urban Policy']
    assert metadata['journal'] == 'Housing Studies'
    assert metadata['publication_date'] == '2026-01-15'


@patch('requests.get')
def test_fetch_from_openalex(mock_get, fetcher, sample_article):
    """Test fetching metadata from OpenAlex API"""
    # Mock OpenAlex API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'abstract': 'This is a test abstract from OpenAlex.',
        'authorships': [
            {'author': {'display_name': 'John Doe'}},
            {'author': {'display_name': 'Jane Smith'}}
        ],
        'keywords': [
            {'display_name': 'housing policy'},
            {'display_name': 'urban development'}
        ],
        'primary_location': {
            'source': {'display_name': 'Housing Studies'}
        },
        'publication_date': '2026-01-15'
    }
    mock_get.return_value = mock_response
    
    metadata = fetcher._fetch_from_openalex(sample_article['doi'])
    
    assert metadata is not None
    assert metadata['abstract'] == 'This is a test abstract from OpenAlex.'
    assert len(metadata['authors']) == 2
    assert 'John Doe' in metadata['authors']
    assert len(metadata['keywords']) == 2
    assert metadata['journal'] == 'Housing Studies'


def test_fetch_metadata_no_doi(fetcher):
    """Test fetching metadata for article without DOI"""
    article_no_doi = {
        'title': 'Article Without DOI',
        'url': 'https://example.com/article',
        'doi': None
    }
    
    result = fetcher.fetch_metadata(article_no_doi)
    
    # Should return article with empty metadata fields
    assert result['abstract'] is None
    assert result['authors'] == []
    assert result['keywords'] == []


def test_clean_abstract(fetcher):
    """Test abstract cleaning function"""
    # HTML tags
    assert 'test abstract' in fetcher._clean_abstract('<p>test abstract</p>')
    
    # Abstract prefix
    assert fetcher._clean_abstract('Abstract: test abstract') == 'test abstract'
    assert fetcher._clean_abstract('ABSTRACT test abstract') == 'test abstract'
    
    # Whitespace normalization
    assert fetcher._clean_abstract('test   \n  abstract') == 'test abstract'
    
    # None input
    assert fetcher._clean_abstract(None) is None
    assert fetcher._clean_abstract('') is None


def test_extract_authors(fetcher):
    """Test author extraction from Crossref format"""
    author_data = [
        {'given': 'John', 'family': 'Doe'},
        {'given': 'Jane', 'family': 'Smith'},
        {'family': 'Organization'}  # No given name
    ]
    
    authors = fetcher._extract_authors(author_data)
    
    assert len(authors) == 3
    assert 'John Doe' in authors
    assert 'Jane Smith' in authors
    assert 'Organization' in authors


def test_format_date(fetcher):
    """Test date formatting from date parts"""
    assert fetcher._format_date([2026]) == '2026'
    assert fetcher._format_date([2026, 1]) == '2026-01'
    assert fetcher._format_date([2026, 1, 15]) == '2026-01-15'
    assert fetcher._format_date([]) == ''


def test_fetch_batch(fetcher, sample_article):
    """Test batch fetching of metadata"""
    articles = [sample_article] * 3
    
    with patch.object(fetcher, 'fetch_metadata') as mock_fetch:
        mock_fetch.return_value = {**sample_article, 'abstract': 'Test'}
        
        results = fetcher.fetch_batch(articles)
        
        assert len(results) == 3
        assert mock_fetch.call_count == 3


def test_get_cache_stats(fetcher):
    """Test cache statistics"""
    stats = fetcher.get_cache_stats()
    
    assert 'total_cached' in stats
    assert 'cache_file' in stats
    assert 'cache_size_kb' in stats
    assert stats['total_cached'] == 0


@patch('requests.get')
def test_api_error_handling(mock_get, fetcher, sample_article):
    """Test handling of API errors"""
    # Mock API error
    mock_get.side_effect = Exception("API Error")
    
    metadata = fetcher._fetch_from_crossref(sample_article['doi'])
    
    # Should return None on error
    assert metadata is None


@patch('requests.get')
def test_rate_limiting(mock_get, fetcher, sample_article):
    """Test that rate limiting is enforced"""
    import time
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'message': {}}
    mock_get.return_value = mock_response
    
    start = time.time()
    
    # Make 3 requests
    for _ in range(3):
        fetcher._fetch_from_crossref(sample_article['doi'])
    
    elapsed = time.time() - start
    
    # Should take at least 0.2 seconds (3 requests * 0.1s interval - 1 interval)
    assert elapsed >= 0.2
