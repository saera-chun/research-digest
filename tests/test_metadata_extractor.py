"""
Tests for Metadata Extractor
"""

from src.analysers.metadata_extractor import extract_geography, extract_methods, extract_stakeholders, extract_all


def test_extract_from_title():
    article = {'title': 'Housing policy in Auckland: impacts on renters', 'keywords': [], 'abstract': ''}
    geo = extract_geography(article)
    assert 'Auckland' in geo


def test_extract_from_keywords():
    article = {'title': '', 'keywords': ['qualitative gis', 'counter-mapping'], 'abstract': ''}
    methods = extract_methods(article)
    # 'qualitative gis' is an alias under 'counter-mapping'
    assert 'counter-mapping' in methods


def test_extract_from_abstract():
    article = {'title': '', 'keywords': [], 'abstract': 'This paper uses interviews and kaupapa maori approaches.'}
    methods = extract_methods(article)
    stakeholders = extract_stakeholders(article)
    assert 'kaupapa-maori' in methods


def test_hyphen_and_case_normalization():
    article = {'title': 'Counter-Mapping and Qualitative-GIS in urban research', 'keywords': [], 'abstract': ''}
    methods = extract_methods(article)
    assert 'counter-mapping' in methods


def test_extract_all_returns_all_fields():
    article = {'title': 'Tenure insecurity in Wellington and Rotorua', 'keywords': ['surveys'], 'abstract': ''}
    all_ = extract_all(article)
    assert 'Wellington' in all_['geography']
    assert 'Rotorua' in all_['geography'] or 'Rotorua' in all_['geography']
    assert 'survey' in ' '.join(all_['methods']) or 'survey-data' in all_['methods']
