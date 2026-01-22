"""
Tests for dictionaries and edge cases
"""

from src.analysers.dictionaries import GEOGRAPHY_KEYWORDS


def test_geography_contains_auckland():
    assert 'Auckland' in GEOGRAPHY_KEYWORDS
    assert 'auckland' in GEOGRAPHY_KEYWORDS['Auckland']


def test_policy_phrase_not_in_geography():
    # Ensure policy-related phrases are not accidentally present in geography aliases
    for aliases in GEOGRAPHY_KEYWORDS.values():
        assert 'emergency housing' not in aliases


def test_national_not_in_geography():
    # Ensure 'national' isn't present in geography aliases
    for aliases in GEOGRAPHY_KEYWORDS.values():
        assert 'national' not in aliases


def test_international_comparators_present():
    # Check a few international comparator entries
    assert 'California' in GEOGRAPHY_KEYWORDS
    assert 'san francisco' in GEOGRAPHY_KEYWORDS['California']
    assert 'Vienna' in GEOGRAPHY_KEYWORDS
    assert 'wien' in GEOGRAPHY_KEYWORDS['Vienna']


def test_method_keywords_updated():
    from src.analysers import dictionaries as dicts

    # Basic presence checks
    assert 'phenomenology-neo' in dicts.METHOD_KEYWORDS
    assert 'phenomenology-general' in dicts.METHOD_KEYWORDS
    assert 'lived experience' in dicts.METHOD_KEYWORDS['phenomenology-general']

    # NZ-specific methods
    assert 'kaupapa-maori' in dicts.METHOD_KEYWORDS
    assert 'kaupapa maori' in dicts.METHOD_KEYWORDS['kaupapa-maori']

    # Ensure scale keywords were removed
    assert not hasattr(dicts, 'SCALE_KEYWORDS')
