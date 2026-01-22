# Research Digest 📚

Personal system for staying on top of academic literature with automated daily digest

## What It Does

**Daily (5 AM):**
- 📰 Fetches articles from 13 journal RSS feeds
- 🔍 Enriches with metadata (Crossref → OpenAlex APIs)
- 📊 Keyword-based ranking (transparent scoring)
- 📧 Sends top 15 articles with total count

**You Reply:**
- 📱 Email reply with tier codes: `1F, 2A, 3M, 4S`
  - **F** = Full read (Zotero + Obsidian note)
  - **A** = Abstract scan (Obsidian note only)
  - **M** = Methodology ref (Obsidian note only)
  - **S** = Skip (seen.json only, no notes)
  - **No response** = Reappears tomorrow
- ⚙️ Auto-processed every 2 hours until 3 PM

**Creates:**
- 📝 Obsidian notes (F/A/M tiers) with structured frontmatter
- 🏷️ Auto-extracted metadata: geography, methods, stakeholders
- 📚 Zotero entries (F tier only, avoids bloat)
- 🔗 Automatic linking via Zotero Integration plugin

**Weekly & Monthly:**
- 📊 Backlog analysis (Saturday)
- 📈 Field trends & reading insights (Monthly)

## Tech Stack

- Python 3.9+ (automation)
- Google Gemini (AI analysis)
- Obsidian (knowledge base)
- Zotero (references)
- iCloud Mail (delivery)

## Status

**Phase 1: Core Pipeline - CURRENT (Week 1-2)**
- ✅ RSS Fetcher - 13 journals, ~500 articles/fetch, RSS summary extraction
- ✅ Deduplicator - DOI+URL dual tracking, 314 entries from manual curation
- ✅ Metadata Fetcher - Crossref → OpenAlex → RSS fallback, 30-day caching
- 📋 **Next:** Article Ranker - Keyword scoring + metadata extraction

**Phase 2: Configuration & Output (Week 3-4)**
- 📋 Config system (boost_keywords, paths, API keys)
- 📋 Metadata extractor (geography, methods, stakeholders)
- 📋 Obsidian Writer (structured notes with frontmatter)
- 📋 Zotero integration (PyZotero, F tier only)

**Phase 3: User Interface (Week 5)**
- 📋 Email Handler (iCloud SMTP/IMAP)
- 📋 Reply Parser & Processor (F/A/M/S selections)
- 📋 Email templates (HTML with styling)

**Phase 4: Orchestration (Week 6)**
- 📋 Main Pipeline (wire all modules)
- 📋 Scheduler (launchd, 5 AM daily)
- 📋 Error handling & logging

**Phase 5: AI Analysis (Week 7-8)**
- 📋 Weekly email (Gemini backlog themes)
- 📋 Monthly email (field trends)

**Phase 6: Enhancements (Week 9-10)**
- 📋 Enhanced Obsidian features (author pages, MOC updates)
- 📋 PDF fetching (Open Access)
- 📋 Advanced Zotero features

**Timeline:** ~10 weeks to production, currently ~15% complete

## Architecture

### Data Flow
```
RSS Feeds → Metadata APIs → AI Analysis → Email Digest
                                             ↓
                                    User Reply (F/A/M/N/S)
                                             ↓
                              ┌──────────────┴──────────────┐
                              ↓                             ↓
                    Obsidian Notes                   Zotero Library
                    (all tiers)                      (FULL only)
```

### File Structure
```
data/
├── seen.json              # All scored articles (F/A/M/S) with tier info
└── doi_cache.json         # API response cache (30-day expiry)

Obsidian vault (single source of truth):
├── Papers/                # All article notes (F/A/M tiers)
└── MOCs/                  # Methodology maps of content

Note: Unscored articles not added to seen.json → reappear tomorrow
Note: Queues managed via Obsidian dataview queries on status field
```

### Email Structure

**Daily (Simple - Build Habit):**
```
📬 RESEARCH DIGEST - 22 January 2026
TOP 15 ARTICLES (208 total unread)

1. Housing policy and tenure security in Auckland
   Urban Studies • housing-policy, tenure-security

[... items 2-15 ...]

REPLY WITH: 1F, 2A, 3M, 4S (or "SHOW ALL")
```

**Weekly (Saturday - Backlog Nudge):**
- Vault stats, emerging themes (AI), oldest articles, reading suggestions

**Monthly (Field Trends):**
- Reading stats, hot topics, methodology landscape, geographic coverage

## Research Focus

Currently tracking journals in:
- Housing Policy & Urban Governance
- Critical Urban Theory  
- Data & Urban Analytics
- Spatial & Environmental Design
- Lived Space, Atmospheres & Experience