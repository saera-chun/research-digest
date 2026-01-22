"""
Backlog Manager

Manages queued articles for F/A/M tiers and their processing state.
Stores backlog in `data/backlog.json` as a dictionary mapping article_id -> metadata.

API:
 - add_to_backlog(article: dict, tier: str, note: Optional[str]) -> article_id
 - list_backlog(tier: Optional[str]=None, status: Optional[str]=None) -> List[dict]
 - mark_processed(article_id: str, status: str, note: Optional[str]=None)
 - remove(article_id: str)
 - get_stats() -> Dict

Behavior mirrors patterns in Deduplicator for ID selection and persistence.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BacklogManager:
    """Manage backlog of queued articles"""

    def __init__(self, backlog_file: str = "data/backlog.json"):
        self.backlog_file = Path(backlog_file)
        self.backlog = self._load_backlog()

    def _load_backlog(self) -> Dict[str, Dict]:
        if not self.backlog_file.exists():
            logger.info(f"Backlog file not found, starting fresh: {self.backlog_file}")
            return {}

        try:
            with open(self.backlog_file, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} backlog entries")
            return data
        except json.JSONDecodeError:
            logger.error(f"Corrupted backlog file, starting fresh: {self.backlog_file}")
            return {}

    def _save_backlog(self):
        self.backlog_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.backlog_file, 'w') as f:
            json.dump(self.backlog, f, indent=2)
        logger.info(f"Saved {len(self.backlog)} backlog entries")

    def _get_article_id(self, article: Dict) -> str:
        if article.get('doi'):
            return f"doi:{article['doi']}"
        return f"url:{article.get('url', '')}"

    def add_to_backlog(self, article: Dict, tier: str = 'A', note: Optional[str] = None) -> str:
        """Add an article to the backlog. Returns article_id."""
        article_id = self._get_article_id(article)

        entry = self.backlog.get(article_id, {})

        # Merge minimal metadata
        entry.update({
            'title': article.get('title'),
            'doi': article.get('doi'),
            'url': article.get('url'),
            'tier': tier,
            'status': entry.get('status', 'queued'),
            'date_added': entry.get('date_added', datetime.now().strftime('%Y-%m-%d')),
            'note': note or entry.get('note')
        })

        self.backlog[article_id] = entry
        self._save_backlog()
        logger.info(f"Added to backlog: {article_id} ({tier})")

        return article_id

    def list_backlog(self, tier: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        results = []
        for article_id, entry in self.backlog.items():
            if tier and entry.get('tier') != tier:
                continue
            if status and entry.get('status') != status:
                continue
            results.append({**entry, 'id': article_id})
        return results

    def mark_processed(self, article_id: str, status: str = 'processed', note: Optional[str] = None):
        if article_id not in self.backlog:
            raise KeyError(f"Article not in backlog: {article_id}")

        self.backlog[article_id]['status'] = status
        if note:
            self.backlog[article_id]['note'] = note
        self.backlog[article_id]['date_processed'] = datetime.now().strftime('%Y-%m-%d')
        self._save_backlog()
        logger.info(f"Marked {article_id} as {status}")

    def remove(self, article_id: str):
        if article_id in self.backlog:
            del self.backlog[article_id]
            self._save_backlog()
            logger.info(f"Removed {article_id} from backlog")

    def get_stats(self) -> Dict[str, int]:
        total = len(self.backlog)
        by_tier: Dict[str, int] = {}
        by_status: Dict[str, int] = {}

        for entry in self.backlog.values():
            by_tier[entry.get('tier', 'N/A')] = by_tier.get(entry.get('tier', 'N/A'), 0) + 1
            by_status[entry.get('status', 'queued')] = by_status.get(entry.get('status', 'queued'), 0) + 1

        return {'total': total, 'by_tier': by_tier, 'by_status': by_status}
