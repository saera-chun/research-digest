"""
Metadata Extractor

Extracts geography, methods, and stakeholders from article text fields
using dictionary-based matching with normalization and word-boundary checks.
"""

import re
from typing import Dict, List

from .dictionaries import GEOGRAPHY_KEYWORDS, METHOD_KEYWORDS, STAKEHOLDER_KEYWORDS


def _normalize(text: str) -> str:
    if not text:
        return ""
    # Lowercase, replace hyphens/underscores with spaces, normalize whitespace
    text = text.lower()
    text = re.sub(r'[_\-]+', ' ', text)
    text = re.sub(r"[\u2018\u2019\u201c\u201d]", "'", text)  # normalize quotes
    text = re.sub(r'[^\w\s\u0100-\u017f]', ' ', text)  # remove punctuation but keep unicode letters
    return ' '.join(text.split())


def _match_keywords(text: str, dictionary: Dict[str, List[str]]) -> List[str]:
    if not text:
        return []

    text_norm = _normalize(text)
    matches = []

    for canonical, aliases in dictionary.items():
        for alias in aliases:
            # Normalize alias similarly and match as word-boundary phrase
            alias_norm = _normalize(alias)
            # Allow simple plural variants (survey -> surveys) by accepting common plural endings
            pattern = r'\b' + re.escape(alias_norm) + r'(?:s|es|ies)?\b'
            if re.search(pattern, text_norm):
                matches.append(canonical)
                break

    return matches


def extract_geography(article: Dict) -> List[str]:
    """Extract geography tags from article fields (title, keywords, abstract)."""
    sources = []
    title = article.get('title', '')
    keywords = ' '.join(article.get('keywords', []) or [])
    abstract = article.get('abstract', '') or ''

    # Priority: title -> keywords -> abstract
    for source in (title, keywords, abstract):
        found = _match_keywords(source, GEOGRAPHY_KEYWORDS)
        for f in found:
            if f not in sources:
                sources.append(f)
        if sources:
            break

    return sources


def extract_methods(article: Dict) -> List[str]:
    title = article.get('title', '')
    keywords = ' '.join(article.get('keywords', []) or [])
    abstract = article.get('abstract', '') or ''

    methods = []
    for source in (title, keywords, abstract):
        found = _match_keywords(source, METHOD_KEYWORDS)
        for f in found:
            if f not in methods:
                methods.append(f)
        if methods:
            break

    return methods


def extract_stakeholders(article: Dict) -> List[str]:
    title = article.get('title', '')
    keywords = ' '.join(article.get('keywords', []) or [])
    abstract = article.get('abstract', '') or ''

    stakeholders = []
    for source in (title, keywords, abstract):
        found = _match_keywords(source, STAKEHOLDER_KEYWORDS)
        for f in found:
            if f not in stakeholders:
                stakeholders.append(f)
        if stakeholders:
            break

    return stakeholders


def extract_all(article: Dict) -> Dict[str, List[str]]:
    return {
        'geography': extract_geography(article),
        'methods': extract_methods(article),
        'stakeholders': extract_stakeholders(article),
    }
