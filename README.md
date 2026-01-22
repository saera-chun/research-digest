# Research Digest 📚

Personal system for staying on top of academic literature with automated daily digest

## What It Does

**Morning (5 AM automated):**
- 📰 Fetches articles from journal RSS feeds
- 📊 Rule-based ranking shows top 15 (AI learning in Phase 2+)
- 📧 Sends digest with NEW articles + BACKLOG insights

**Throughout the Day:**
- 📱 Review and reply with tier codes: `1F, 2A, 3M, 4S`
  - **F** = Full read (deep dive + PDF)
  - **A** = Abstract only (quick scan)
  - **M** = Methodology only (file for reference)
  - **S** = Skip (mark as seen/ignore)
  - **No response** = Article reappears tomorrow
- ⚙️ System processes selections automatically

**Creates:**
- 📝 Skeleton notes in Obsidian (all tiers, progressive enhancement)
- 📅 Daily digest note with AI summary
- 🏷️ Auto-updated methodology MOCs
- 📚 Zotero entries (FULL tier only)

**Plus:**
- 🔍 AI trend analysis by journal
- 🧩 Thematic clustering of backlog
- 📊 Cross-cutting theme detection
- 🗃️ Separate queues for FULL/ABSTRACT reads

## Tech Stack

- Python 3.9+ (automation)
- Google Gemini (AI analysis)
- Obsidian (knowledge base)
- Zotero (references)
- iCloud Mail (delivery)

## Status

**Phase 1: Data Collection (Week 1-2)**
- ✅ RSS Fetcher - 13 journals, ~500 articles/fetch
- ✅ Deduplicator - DOI+URL dual tracking
- 🚧 Metadata Fetcher - Crossref/OpenAlex/Elsevier APIs
- 📋 Backlog Manager - Multi-tier queue system

**Phase 2: AI Analysis (Week 3-4)**
- 📋 Content filtering & relevance scoring
- 📋 Trend analysis by journal
- 📋 Thematic clustering of backlog
- 📋 Methodology detection

**Phase 3: User Interface (Week 5-6)**
- 📋 Email handler (iCloud SMTP/IMAP)
- 📋 Reply parser (`1F, 2A, 3M, 4S` format)
- 📋 CLI interface with hotkeys

**Phase 4: Output (Week 7-8)**
- 📋 Obsidian writer (skeleton notes, templates)
- 📋 Zotero integration (FULL tier)

**Phase 5: Orchestration (Week 9-10)**
- 📋 Main pipeline + scheduler
- 📋 Error handling & logging

**Timeline:** ~10 weeks to production

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
├── seen.json              # All scored articles (F/A/M/S)
├── queued_full.json       # Deep read queue (F)
├── queued_abstract.json   # Abstract queue (A)
├── methodologies.json     # Methodology library (M)
└── doi_cache.json         # API response cache

Note: Unscored articles are not added to seen.json, so they 
reappear in tomorrow's fetch until you make a decision
```

### Email Digest Structure
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆕 NEW ARTICLES (15 shown, 35 filtered)
🤖 AI Trend Analysis
   • Housing Studies: climate adaptation surge...
   • Urban Studies: ML dominates, mobility patterns...
[Articles 1-15]
Reply: 1F, 2A, 3M, 4S or "SHOW ALL"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 BACKLOG STATUS
🔥 FULL QUEUE (5)
   🤖 Clusters: Urban resilience (3), Affordability (2)
📄 ABSTRACT QUEUE (18)
   🤖 Cross-cutting: "Community voice" in 6 papers
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Research Focus

Currently tracking journals in:
- Housing Policy & Urban Governance
- Critical Urban Theory  
- Data & Urban Analytics
- Spatial & Environmental Design
- Lived Space, Atmospheres & Experience