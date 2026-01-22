# Progress Log

## 2026-01-19

### Proposed Structure

```
research-digest/
├── data/
├── logs/
├── src/
│   ├── analysers/
│   ├── collectors/
│   ├── integrations/
│   ├── interfaces/
│   ├── utils/
│   └── writers/
├── templates/
│   ├── email/
│   └── obsidian/
└── tests/
```

### Setup

```bash
# create repo
cd /Users/saerachun/projects
mkdir research-digest && cd research-digest
git init

# create folders
mkdir -p data
mkdir -p logs
mkdir -p src/analysers
mkdir -p src/collectors
mkdir -p src/integrations
mkdir -p src/interfaces
mkdir -p src/utils
mkdir -p src/writers
mkdir -p templates/email
mkdir -p templates/obsidian
mkdir -p tests

# create python packages
touch src/__init__.py
touch src/analysers/__init__.py
touch src/collectors/__init__.py
touch src/integrations/__init__.py
touch src/interfaces/__init__.py
touch src/utils/__init__.py
touch src/writers/__init__.py
touch tests/__init__.py
touch data/.gitkeep
touch logs/.gitkeep

# push to GitHub
git add .
git commit -m "Initial project structure"
git remote add origin https://github.com/saera-chun/research-digest.git
git push -u origin master
```

### Created README.md and started a progress log
### Added .gitignore
### Added requirements.txt

``` bash
# create virtual environment
python3 -m venv venv
source venv/bin/activate

# install packages
pip install -r requirements.txt
```

### Added package metadata to __init__.py files

- `src/__init__.py` - Package version, author, description
- Module-specific files - Docstrings with commented import roadmap for future modules

**__init__.py** (main package):
```python
"""
Research Digest - Automated academic literature management system

Fetches articles from RSS feeds, analyses them with AI, and creates
structured notes in Obsidian with Zotero integration.
"""

__version__ = "0.1.0"
__author__ = "Saera Chun"

__title__ = "research-digest"
__description__ = "Automated system for fetching, and organising academic articles"
__url__ = "https://github.com/saera-chun/research-digest"
```


**__init__.py** (collectors):
```python
"""
Data collection modules for fetching articles and metadata
"""
# Imports will be added as modules are created:
# from .rss_fetcher import RSSFetcher
# from .metadata_fetcher import MetadataFetcher
# from .web_scraper import WebScraper
```

**__init__.py** (analysers):
```python
"""
AI analysis modules for methodology detection and tagging
"""
# from .ai_analyzer import AIAnalyzer
# from .methodology_detector import MethodologyDetector
# from .tagger import Tagger
```

**__init__.py** (intefaces):
```python
"""
User interface modules for email and CLI interaction
"""
# from .email_handler import EmailHandler
# from .reply_parser import ReplyParser
# from .cli_interface import CLIInterface
```

**__init__.py** (writers):
```python
"""
Output generation modules for Obsidian notes
"""
# from .obsidian_writer import ObsidianWriter
# from .template_engine import TemplateEngine
```

**__init__.py** (integrations):
```python
"""
External service integrations (Zotero, APIs)
"""
# from .zotero_sync import ZoteroSync
```

**__init__.py** (utils):
```python
"""
Utility functions and helpers
"""
# from .cache import Cache
# from .logger import setup_logger
# from .helpers import *
```

**__init__.py** (tests):
```python
"""
Test suite for research-digest
"""
```

### Configuration and setup

1. Installed Playwright browsers
```bash
python -m playwright install chromium
```

2. Created example `config.json` and `feeds.txt`


### Phase 1: Data Collection 

Phase 1: Build & Test Core Collectors (one at a time)

1. ✅ **RSS Fetcher** - Built and tested
   - Created `src/collectors/rss_fetcher.py`
   - Loads feed URLs from `feeds.txt` (ignores comments, strips whitespace)
   - Fetches articles using `feedparser.parse()`
   - Extracts: title, URL, DOI, published_date, feed_title, feed_url
   - DOI extraction: checks `prism_doi` field, then regex from URL
   - Journal title cleaning: regex removes publisher prefixes (tandf:, SAGE Publications:) and suffixes (: Table of Contents)
   - Returns list of article dictionaries
   - **Tests:** `tests/test_rss.py`
     - Loads feeds from file
     - Fetches all articles (~500 from 13 feeds)
     - Validates article structure and required fields
     - Tests journal title cleaning with regex patterns
     - Tests single feed fetching
```bash
python -m pytest tests/test_rss.py -v
```

2. ✅ **Deduplicator** - Built and tested
   - Created `src/utils/deduplicator.py`
   - Tracks seen articles in `data/seen.json` permanently (no time limit)
   - Uses DOI as primary identifier, URL as fallback
   - Format: `{"doi:10.1234/abc": "2026-01-19", "url:https://...": "2026-01-20"}`
   - `filter_new()`: checks both DOI and URL to prevent duplicates (handles case where article first appears without DOI, then with DOI later)
   - `mark_as_seen()`: adds article IDs to dictionary with current date, saves to JSON
   - `get_stats()`: returns total count, DOI count, URL count
   - **Tests:** `tests/test_deduplicator.py`
     - New deduplicator starts empty
     - Filters new vs seen articles correctly
     - Persists across instances (reloads from file)
     - DOI-based identification (recognizes same article via DOI despite different URLs)
     - URL→DOI upgrade prevention (article first seen by URL, then with DOI, not duplicated)
     - Statistics reporting
```bash
python -m pytest tests/test_deduplicator.py -v
```


## 2026-01-21

### Manual feed curation

- Reviewed all 13 feeds: 11 with articles, feeds 6/9/13 empty
- Built initial `seen.json` with 314 entries  
- Fixed Feed 8 URL error (`jc=eupa` → `jc=eura`)
- Created helper scripts for feed review and testing

### Full pipeline test

- RSS + deduplication: 517 fetched → 314 seen → 208 new
- All tests passing


## 2026-01-22

### Architecture refinement

After initial curation revealed 200+ interesting articles, refined system design:

**Key changes:**
- Multi-tier selection: FULL (deep read) / ABSTRACT (scan) / METHOD (file only) / SKIP
- Enhanced email: NEW section (filtered + trends) + BACKLOG section (thematic analysis)
- Queue files: `queued_full.json`, `queued_abstract.json` (unscored articles reappear next day)
- Obsidian: skeleton notes for F/A/M tiers, progressive enhancement
- Selection format: Email reply `"1F, 2A, 3M, 4S"` or CLI with hotkeys

**Filtering approach:**
- Keyword-based ranking: articles scored by matching boost keywords (no exclusions)
- Config structure: `{"boost_keywords": {"spatial_methods": 40, "housing_policy": 40, ...}, "exclude_patterns": []}`
- Pure keyword scoring, transparent and tunable
- AI learning layer optional for future enhancement

**Volume control:**
- Email shows top 15 articles by keyword score
- Header displays total count (e.g., "15 shown, 193 total")
- User can reply "SHOW ALL" to see full list
- No auto-skip: unscored articles reappear until scored
- Simple approach for beta testing, adjust based on usage patterns

See README.md for full design details.


### Phase 1: Data Collection (Cont.)


3. ✅ **Metadata Fetcher** - Built and tested
   - Created `src/collectors/metadata_fetcher.py`
   - Fetches metadata from Crossref API (primary) and OpenAlex API (fallback)
   - Extracts: canonical title (overrides RSS), authors, keywords, journal name, publication date
   - 30-day caching in `data/doi_cache.json` (avoids redundant API calls)
   - Rate limiting: 10 req/sec (conservative, polite to free APIs)
   - Graceful degradation: returns empty fields if APIs fail
   - **Tests:** `tests/test_metadata_fetcher.py`
     - Cache persistence and retrieval
     - Crossref and OpenAlex API parsing
     - Abstract cleaning and author extraction
     - Rate limiting enforcement
     - Error handling
```bash
python -m pytest tests/test_metadata_fetcher.py -v
```
   - **Note:** Abstracts not available via free APIs (expected limitation). 15% of articles lack DOIs (ScienceDirect). Keyword scoring uses title (always) + keywords (when available).



- 📋 Article Ranker - Keyword-based scoring
- 📋 Backlog Manager - Multi-tier queue system

**Phase 2: AI Analysis (Week 3-4)**
- 📋 Content filtering & relevance scoring
- 📋 Trend analysis by journal
- 📋 Thematic clustering of backlog
- 📋 Methodology detection

**Phase 3: User Interface (Week 5-6)**
- 📋 Email handler (iCloud SMTP/IMAP)
- 📋 Reply parser (`1F, 2A, 3M, 4N, 5S` format)
- 📋 CLI interface with hotkeys

**Phase 4: Output (Week 7-8)**
- 📋 Obsidian writer (skeleton notes, templates)
- 📋 Zotero integration (FULL tier)

**Phase 5: Orchestration (Week 9-10)**
- 📋 Main pipeline + scheduler
- 📋 Error handling & logging