"""
Article Ranker Module

Scores and ranks articles based on keyword matching against user-defined
boost keywords. Pure keyword-based scoring with no journal weighting or
recency bias - transparent and tunable.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class ArticleRanker:
    """Ranks articles by keyword matching score"""
    
    def __init__(self, boost_keywords: Dict[str, int]):
        """
        Initialize ranker with boost keyword weights
        
        Args:
            boost_keywords: Dict mapping keyword strings to score weights
                           e.g., {"housing-policy": 40, "spatial-methods": 40}
        """
        self.boost_keywords = boost_keywords
        # Normalize keywords to lowercase for case-insensitive matching
        self.boost_keywords_lower = {k.lower(): v for k, v in boost_keywords.items()}
    
    def rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Score and rank articles by keyword matching
        
        Args:
            articles: List of article dicts with title, keywords, abstract fields
        
        Returns:
            List of article dicts sorted by score (highest first),
            with 'score' field added to each article
        """
        scored_articles = []
        
        for article in articles:
            score = self._calculate_score(article)
            article_with_score = {**article, 'score': score}
            scored_articles.append(article_with_score)
        
        # Sort by score (highest first)
        ranked = sorted(scored_articles, key=lambda x: x['score'], reverse=True)
        
        if ranked:
            logger.info(f"Ranked {len(ranked)} articles (scores: {ranked[0]['score']} to {ranked[-1]['score']})")
        else:
            logger.info("No articles to rank")
        
        return ranked
    
    def _calculate_score(self, article: Dict) -> int:
        """
        Calculate keyword matching score for an article
        
        Searches in:
        1. Title (always present)
        2. Keywords from API (when available)
        3. Abstract (when available)
        
        Returns:
            Total score from all matching boost keywords
        """
        score = 0
        
        # Build searchable text from available fields
        title = article.get('title', '').lower()
        keywords = article.get('keywords', [])
        abstract = article.get('abstract', '') or ''
        
        # Combine keywords into searchable string
        keywords_text = ' '.join(keywords).lower() if keywords else ''
        abstract_text = abstract.lower()
        
        # Combined search text - normalize hyphens to spaces for flexible matching
        search_text = f"{title} {keywords_text} {abstract_text}".replace('-', ' ')
        
        # Match against boost keywords
        for boost_keyword, weight in self.boost_keywords_lower.items():
            # Normalize boost keyword (replace hyphens with spaces)
            normalized_keyword = boost_keyword.replace('-', ' ')
            
            # Case-insensitive partial matching
            # "housing policy" matches "housing-policy", "housing policies", etc.
            if normalized_keyword in search_text:
                score += weight
                logger.debug(f"Match: '{boost_keyword}' (+{weight}) in {article.get('title', 'Unknown')[:50]}")
        
        return score
    
    def get_top_articles(self, articles: List[Dict], n: int = 15) -> List[Dict]:
        """
        Get top N ranked articles
        
        Args:
            articles: List of articles to rank
            n: Number of top articles to return (default 15 for daily email)
        
        Returns:
            Top N articles sorted by score
        """
        ranked = self.rank_articles(articles)
        return ranked[:n]
    
    def get_statistics(self, articles: List[Dict]) -> Dict:
        """
        Get ranking statistics for articles
        
        Args:
            articles: List of ranked articles (with 'score' field)
        
        Returns:
            Dict with min, max, mean, median scores
        """
        if not articles:
            return {'min': 0, 'max': 0, 'mean': 0, 'median': 0}
        
        scores = [a.get('score', 0) for a in articles]
        scores_sorted = sorted(scores)
        
        return {
            'min': scores_sorted[0],
            'max': scores_sorted[-1],
            'mean': sum(scores) / len(scores),
            'median': scores_sorted[len(scores) // 2],
            'total_articles': len(articles),
            'zero_score': sum(1 for s in scores if s == 0)
        }
