"""
Tests for Backlog Manager
"""

import json
from pathlib import Path
import pytest

from src.utils.backlog_manager import BacklogManager


@pytest.fixture
def temp_backlog(tmp_path):
    f = tmp_path / "test_backlog.json"
    return str(f)


@pytest.fixture
def manager(temp_backlog):
    return BacklogManager(backlog_file=temp_backlog)


def sample_article(doi='10.1000/test1'):
    return {
        'title': 'Test Article',
        'url': 'https://example.com/test1',
        'doi': doi
    }


def test_add_and_list(manager):
    art = sample_article()
    aid = manager.add_to_backlog(art, tier='F', note='important')

    listed = manager.list_backlog()
    assert len(listed) == 1
    assert listed[0]['id'] == aid
    assert listed[0]['tier'] == 'F'
    assert listed[0]['note'] == 'important'


def test_mark_processed_and_stats(manager):
    art = sample_article('10.1000/test2')
    aid = manager.add_to_backlog(art, tier='A')

    stats_before = manager.get_stats()
    assert stats_before['total'] == 1

    manager.mark_processed(aid, status='reviewed', note='checked')

    listed = manager.list_backlog(status='reviewed')
    assert len(listed) == 1
    assert listed[0]['status'] == 'reviewed'
    assert listed[0]['note'] == 'checked'


def test_persistence(temp_backlog):
    manager1 = BacklogManager(backlog_file=temp_backlog)
    aid = manager1.add_to_backlog(sample_article('10.1000/test3'), tier='M')

    manager2 = BacklogManager(backlog_file=temp_backlog)
    assert aid in [e['id'] for e in manager2.list_backlog()]


def test_remove(manager):
    art = sample_article('10.1000/test4')
    aid = manager.add_to_backlog(art, tier='S')
    manager.remove(aid)
    assert manager.get_stats()['total'] == 0
