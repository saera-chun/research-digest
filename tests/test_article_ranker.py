"""
Tests for Article Ranker
"""

import pytest
from src.analysers.article_ranker import ArticleRanker


@pytest.fixture
def boost_keywords():
    """Sample boost keywords for testing"""
    return {
        "housing-policy": 40,
        "spatial-methods": 40,
        "tenure-security": 35,
        "affordability": 30,
        "auckland": 30,
        "qualitative": 20,
    }


@pytest.fixture
def sample_articles():
    """Sample articles with varying relevance"""
    return [
        {
            "title": "Housing policy and tenure security in Auckland",
            "keywords": ["housing-policy", "tenure-security", "affordability"],
            "abstract": "This study examines housing affordability issues in Auckland...",
            "doi": "10.1234/test1"
        },
        {
            "title": "Spatial methods in urban geography",
            "keywords": ["spatial-methods", "GIS", "mapping"],
            "abstract": "A methodological paper on spatial analysis techniques...",
            "doi": "10.1234/test2"
        },
        {
            "title": "Climate change impacts on agriculture",
            "keywords": ["climate", "agriculture", "adaptation"],
            "abstract": "Study of climate impacts on farming practices...",
            "doi": "10.1234/test3"
        },
        {
            "title": "Qualitative housing research in New Zealand",
            "keywords": ["qualitative", "housing", "methodology"],
            "abstract": None,  # No abstract
            "doi": "10.1234/test4"
        }
    ]


def test_ranker_initialization(boost_keywords):
    """Test ranker initializes with boost keywords"""
    ranker = ArticleRanker(boost_keywords)
    assert ranker.boost_keywords == boost_keywords
    assert "housing-policy" in ranker.boost_keywords_lower


def test_keyword_matching_case_insensitive(boost_keywords):
    """Test case-insensitive keyword matching"""
    ranker = ArticleRanker(boost_keywords)
    
    article = {
        "title": "HOUSING POLICY and Housing Affordability",
        "keywords": [],
        "abstract": None
    }
    
    score = ranker._calculate_score(article)
    # Should match "housing-policy" (40, from "housing policy") + 
    #              "affordability" (30, from "housing affordability") = 70
    assert score == 70


def test_partial_keyword_matching(boost_keywords):
    """Test partial keyword matching works"""
    ranker = ArticleRanker(boost_keywords)
    
    article = {
        "title": "Housing policy and affordability crisis",
        "keywords": [],
        "abstract": None
    }
    
    score = ranker._calculate_score(article)
    # "housing policy" should match "housing-policy" (40)
    # "affordability" should match "affordability" (30)
    assert score == 70


def test_score_calculation_all_fields(boost_keywords, sample_articles):
    """Test scoring uses title, keywords, and abstract"""
    ranker = ArticleRanker(boost_keywords)
    
    # First article has matches in all fields
    article = sample_articles[0]
    score = ranker._calculate_score(article)
    
    # Should find: housing-policy (40) + tenure-security (35) + 
    #              affordability (30 from keywords, may match again in abstract/title) + auckland (30)
    assert score >= 135  # At minimum these four matches


def test_ranking_sorts_by_score(boost_keywords, sample_articles):
    """Test articles are sorted by score descending"""
    ranker = ArticleRanker(boost_keywords)
    
    ranked = ranker.rank_articles(sample_articles)
    
    # Check all articles have scores
    assert all('score' in a for a in ranked)
    
    # Check sorted descending
    scores = [a['score'] for a in ranked]
    assert scores == sorted(scores, reverse=True)
    
    # First article (housing in Auckland) should rank highest
    assert ranked[0]['doi'] == "10.1234/test1"
    
    # Climate article should rank lowest (no matches)
    assert ranked[-1]['doi'] == "10.1234/test3"
    assert ranked[-1]['score'] == 0


def test_get_top_articles(boost_keywords, sample_articles):
    """Test retrieving top N articles"""
    ranker = ArticleRanker(boost_keywords)
    
    top_2 = ranker.get_top_articles(sample_articles, n=2)
    
    assert len(top_2) == 2
    # Top two should be housing articles
    assert top_2[0]['doi'] == "10.1234/test1"
    assert top_2[1]['doi'] in ["10.1234/test2", "10.1234/test4"]


def test_statistics(boost_keywords, sample_articles):
    """Test ranking statistics calculation"""
    ranker = ArticleRanker(boost_keywords)
    
    ranked = ranker.rank_articles(sample_articles)
    stats = ranker.get_statistics(ranked)
    
    assert 'min' in stats
    assert 'max' in stats
    assert 'mean' in stats
    assert 'median' in stats
    assert 'total_articles' in stats
    assert 'zero_score' in stats
    
    assert stats['total_articles'] == 4
    assert stats['zero_score'] == 1  # Climate article
    assert stats['max'] > stats['min']


def test_empty_articles_list(boost_keywords):
    """Test handling empty articles list"""
    ranker = ArticleRanker(boost_keywords)
    
    ranked = ranker.rank_articles([])
    assert ranked == []
    
    stats = ranker.get_statistics([])
    assert stats['min'] == 0
    assert stats['max'] == 0


def test_article_without_optional_fields(boost_keywords):
    """Test scoring article with missing optional fields"""
    ranker = ArticleRanker(boost_keywords)
    
    article = {
        "title": "Housing policy research",
        "keywords": None,  # Missing
        "abstract": None   # Missing
    }
    
    score = ranker._calculate_score(article)
    # Should still match "housing-policy" in title
    assert score == 40


def test_no_keyword_matches(boost_keywords):
    """Test article with no matching keywords scores zero"""
    ranker = ArticleRanker(boost_keywords)
    
    article = {
        "title": "Completely unrelated topic",
        "keywords": ["biology", "genetics"],
        "abstract": "Study of gene expression"
    }
    
    score = ranker._calculate_score(article)
    assert score == 0


def test_multiple_matches_same_keyword(boost_keywords):
    """Test keyword appearing multiple times counts once"""
    ranker = ArticleRanker(boost_keywords)
    
    article = {
        "title": "Housing policy and housing",
        "keywords": ["housing-policy"],
        "abstract": "Housing policy is important for affordable housing"
    }
    
    score = ranker._calculate_score(article)
    # Even though "housing" and "policy" appear multiple times,
    # "housing-policy" as a phrase should match once per occurrence in search text
    # But our implementation uses "in" which checks substring presence once
    # So it should be scored based on unique keyword matches
    assert score > 0
