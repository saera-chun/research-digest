# Research Digest - System Design

**Last Updated:** 2026-01-22

## 1. Core Goals

- **Primary:** Build daily reading habit (minimum 1 article/day)
- **Secondary:** Create Obsidian research database for academic + policy work
- **Tertiary:** Automate curation pipeline (RSS → AI analysis → structured notes)

## 2. System Flow

```
RSS Feeds (13 journals)
    ↓
Deduplicator (seen.json)
    ↓
Metadata Enrichment (Crossref → OpenAlex → RSS summaries)
    ↓
Keyword Scoring (boost_keywords config)
    ↓
Daily Email (Top 15 ranked, show total count)
    ↓
User Reply (1F, 2A, 3M, 4S)
    ↓
┌─────────────┬──────────────┬──────────────┐
│   F Tier    │   A Tier     │   M Tier     │
│  (Full)     │  (Abstract)  │  (Method)    │
└─────────────┴──────────────┴──────────────┘
    ↓               ↓              ↓
Zotero Entry   Obsidian Only  Obsidian Only
    ↓               ↓              ↓
Obsidian Note  Obsidian Note  Obsidian Note
(via Zotero    (direct)       (direct)
Integration)
```

**S Tier (Skip):** Added to seen.json only, no notes created  
**Unscored:** Not added to seen.json, reappears tomorrow

## 3. Four-Tier Selection System

### F - Full Read
- **Purpose:** Deep engagement, may cite in research
- **Actions:**
  1. Create Zotero entry with metadata
  2. Auto-generate Obsidian note via Zotero Integration plugin
  3. Add to reading queue
  4. Fetch PDF if Open Access (future)
- **Status:** `status: queued-full` → `read`

### A - Abstract Scan
- **Purpose:** Interesting but not immediate priority, review abstract
- **Actions:**
  1. Create Obsidian note directly (no Zotero)
  2. Add to abstract review queue
- **Status:** `status: queued-abstract` → `reviewed`

### M - Methodology Reference
- **Purpose:** File for future methodology reference
- **Actions:**
  1. Create Obsidian note directly
  2. Add to methodology MOC (Map of Content)
  3. Tag with specific methods
- **Status:** `status: methodology-ref`

### S - Skip
- **Purpose:** Not relevant, prevent reappearance
- **Actions:**
  1. Add to seen.json with skip status
  2. No notes created (zero clutter)

## 4. Data Architecture

### Obsidian Note Schema (All Tiers)

```yaml
---
# Academic Metadata (from APIs)
title: "Housing policy and tenure security in Auckland"
authors: [[John Doe]], [[Jane Smith]]
year: 2026
journal: [[Urban Studies]]
doi: 10.1234/example
url: https://doi.org/10.1234/example
keywords: [housing-policy, tenure-security, affordability]  # conceptual only
status: queued-full  # or: queued-abstract, methodology-ref, read, reviewed
date-added: 2026-01-22

# Research Dimensions (auto-extracted from title/keywords/abstract)
geography: [[New Zealand]], [[Auckland]]
methods: [case-study, qualitative, interviews]
stakeholders: [renters, local-government, developers]

# Zotero Integration (F tier only)
zotero-key: ABC123XYZ  # citekey for linking
---

## Summary
[User adds notes here]

## Key Findings

## Methodology Notes

## Relevance to My Research
```

### Zotero Entry Schema (F Tier Only)

**Standard Fields:**
- Title, Authors, Year, Journal, DOI, URL, Abstract (when available)

**Tags:**
- `#source/digest` - Auto-added to all digest entries
- `#priority/F` - Indicates full read tier
- `#scale/micro` or `#scale/meso` or `#scale/macro` - Auto-detected scale
- Custom tags from stakeholders field (e.g., `#stakeholder/renters`)

**Collections:**
- Organisd by journal (auto-created)
- "Research Digest - Queued" collection for unread F-tier papers

### Storage Files

**data/seen.json** - Permanent deduplication record
```json
{
  "doi:10.1234/example": {
    "date_seen": "2026-01-22",
    "tier": "F",
    "title": "Housing policy..."
  },
  "url:https://example.com/article": {
    "date_seen": "2026-01-22",
    "tier": "S",
    "title": "Another article..."
  }
}
```

**data/doi_cache.json** - 30-day API response cache
```json
{
  "10.1234/example": {
    "fetched_at": "2026-01-22T10:30:00",
    "source": "crossref",
    "data": {
      "title": "...",
      "authors": ["..."],
      "keywords": ["..."]
    }
  }
}
```

## 5. Email System (Multi-Cadence)

### Daily Email

**Subject:** `Research Digest - [Date] - [X] Articles`

**Body:**
```
📬 RESEARCH DIGEST
22 January 2026

TOP 15 ARTICLES (208 total unread)

1. Housing policy and tenure security in Auckland
   Journal: Urban Studies • Keywords: housing-policy, tenure-security
   
2. Spatial methods in urban geography
   Journal: Annals AAG • Keywords: spatial-methods, GIS
   
[... items 3-15 ...]

---
REPLY WITH: 1F, 2A, 3M, 4S (or reply "SHOW ALL" for full list)

F = Full read | A = Abstract scan | M = Methodology | S = Skip
```

**Processing:**
- Auto-scans IMAP for replies every 2 hours until 3 pm
- Parses tier selections from email body
- Creates Zotero entries (F tier)
- Creates Obsidian notes (F/A/M tiers)
- Updates seen.json with selections

### Weekly Email (Saturday - Backlog Nudge)

**Subject:** `Research Digest - Weekly Review`

**Content:**
- Vault statistics (X queued-full, Y queued-abstract)
- Emerging themes in queue (AI analysis via Gemini)
- Oldest unread articles (gentle nudge)
- Suggested reading order based on connections
- "This week you marked: 5F, 3A, 1M, 2S"

### Monthly Email (1st of Month - Field Trends)

**Subject:** `Research Digest - [Month] Trends`

**Content:**
- Your reading stats (articles read, completion rate)
- Field hot topics (AI analysis of all January papers)
- Methodology landscape (what methods are trending)
- Geographic coverage (where research is happening)
- Journal breakdown (which journals most productive)

## 6. Keyword Scoring System

### Config Structure (config.json)

```json
{
  "boost_keywords": {
    "phenomenology": 60,
    "lived-experience": 60,
    "hermann-schmitz": 70,
    "counter-mapping": 60,
    "spatial-justice": 50,
    "housing-policy": 30,
    "tenure-security": 35,
    "building-consent": 30,
    "social-housing": 30,
    "mixed-methods": 30,
    "auckland": 15,
    "wellington": 15,
    "new-zealand": 10,
    "affordability": 10
  },
  "email": {
    "smtp_server": "smtp.mail.me.com",
    "smtp_port": 587,
    "imap_server": "imap.mail.me.com",
    "imap_port": 993,
    "email_address": "your-email@icloud.com",
    "send_time": "05:00"
  },
  "obsidian": {
    "vault_path": "/Users/saerachun/Obsidian/Research",
    "papers_folder": "Papers",
    "moc_folder": "MOCs"
  },
  "zotero": {
    "api_key": "your-api-key",
    "library_id": "your-library-id",
    "library_type": "user"
  }
}
```

### Scoring Logic

1. **Match keywords** against: title (required) + API keywords (when available) + abstract (when available)
2. **Case-insensitive partial matching** (e.g., "housing policy" matches "housing-policy", "housing policies")
3. **Sum all matching keyword scores**
4. **Sort by total score** (highest first)
5. **No journal weighting, no recency bias** - pure keyword relevance

### Example Scoring

Article: "Housing affordability and tenure security for renters in Auckland"
- Matches: housing-policy (40) + affordability (30) + tenure-security (35) + auckland (30)
- **Total Score: 135**

Article: "Spatial analysis of urban development patterns"
- Matches: spatial-methods (40)
- **Total Score: 40**

First article ranks higher → appears earlier in daily email

## 7. Metadata Extraction

### Geography Extraction

**Dictionary-based keyword matching:**
```python
GEOGRAPHY_KEYWORDS = {
    "New Zealand": ["new zealand", "aotearoa", "nz"],
    "Auckland": ["auckland", "tāmaki makaurau"],
    "Wellington": ["wellington", "te whanganui-a-tara"],
    "United States": ["united states", "usa", "u.s."],
    "United Kingdom": ["united kingdom", "uk", "u.k.", "britain"],
    # ... expanded per user's research geography
}
```

**Sources:** Title → Keywords → Abstract (in order of availability)

### Methods Extraction

```python
METHOD_KEYWORDS = {
    "case-study": ["case study", "case-study", "case studies"],
    "qualitative": ["qualitative", "interviews", "ethnography", "discourse analysis"],
    "quantitative": ["quantitative", "regression", "statistical analysis", "survey"],
    "mixed-methods": ["mixed methods", "mixed-methods", "triangulation"],
    "phenomenology": ["phenomenology", "phenomenological"],
    "spatial-analysis": ["spatial analysis", "gis", "mapping", "geospatial"]
}
```

### Stakeholders Extraction

```python
STAKEHOLDER_KEYWORDS = {
    "renters": ["tenant", "renter", "rental", "private rented sector", "tenancy"],
    "homeowners": ["homeowner", "owner-occupier", "home ownership"],
    "landlords": ["landlord", "private landlord", "rental provider"],
    "developers": ["developer", "housebuilder", "property developer"],
    "local-government": ["council", "local authority", "municipality", "city government"],
    "national-government": ["central government", "federal", "national policy", "ministry"],
    "planners": ["urban planner", "planning authority", "zoning", "land use planning"],
    "community-groups": ["community organization", "resident association", "advocacy group"],
    "housing-associations": ["social housing", "housing association", "public housing"],
    "private-sector": ["private sector", "market", "commercial"],
    "public-sector": ["public sector", "state", "government intervention"]
}
```

## 8. Implementation Roadmap

### Phase 1: Core Pipeline (Current)
- ✅ RSS Fetcher (with summary extraction)
- ✅ Deduplicator (DOI + URL tracking)
- ✅ Metadata Fetcher (Crossref → OpenAlex → RSS fallback)
- 📋 **Next:** Article Ranker (keyword scoring)

### Phase 2: Configuration & Filtering (Week 3)
- 📋 Config system (load boost_keywords, email settings, paths)
- 📋 Metadata extractor (geography, methods, stakeholders)
- 📋 Article ranker with extraction integration

### Phase 3: Output Generation (Week 4)
- 📋 Obsidian Writer (create notes with frontmatter)
- 📋 Zotero integration (PyZotero, F tier only)
- 📋 Email template generator (HTML with styling)

### Phase 4: User Interface (Week 5)
- 📋 Email Handler (SMTP send, IMAP receive)
- 📋 Reply Parser (parse F/A/M/S selections)
- 📋 Reply Processor (trigger note creation, Zotero sync)

### Phase 5: Orchestration (Week 6)
- 📋 Main Pipeline (wire all modules together)
- 📋 Error handling and logging
- 📋 Scheduler (launchd for 5 AM daily runs)

### Phase 6: AI Analysis (Week 7-8)
- 📋 Weekly email (backlog themes via Gemini)
- 📋 Monthly email (field trends via Gemini)
- 📋 Gemini API integration

### Phase 7: Enhancements (Week 9-10)
- 📋 Enhanced Obsidian features (author pages, MOC updates)
- 📋 PDF fetching (Open Access articles)
- 📋 Advanced Zotero features (tags, collections, notes)
- 📋 CLI interface (optional alternative to email)

## 9. Data Sources & Coverage

### RSS Feeds (13 Journals)
- ~500 articles per fetch
- ~40 new articles per month (steady state)?
- Update frequency: varies by journal (daily to weekly)
- Provides: title, URL, DOI (85%), RSS summary (40-50% from SAGE)

### API Coverage
- **Crossref:** Primary source, ~95% success for DOI articles
- **OpenAlex:** Fallback, ~80% success when Crossref fails
- **Abstracts:** ~0% from APIs (paywalled), ~40-50% from RSS summaries

### Known Limitations
- 15% articles lack DOIs (ScienceDirect) → scored on title only
- No full abstracts from free APIs → rely on RSS summaries + title/keywords
- Semantic Scholar rejected (poor social science coverage)

## 10. Success Metrics

### Beta Phase (Months 1-2)
- Daily email open rate > 80%
- Daily reply rate > 60% (build habit)
- Average 1+ article selected per day
- Backlog stabilises at <100 articles

### Mature Phase (Months 3+)
- Obsidian vault has 100+ structured notes
- Zotero library has 50+ papers (F tier)
- Weekly email insights deemed useful
- Monthly trends inform research direction
- System requires <10 minutes daily maintenance

## 11. Design Principles

1. **Simplicity over features** - Every component must justify its existence
2. **User agency first** - System suggests, user decides (no auto-tagging, no auto-skip)
3. **Obsidian as primary** - Single source of truth for research knowledge
4. **Zotero for serious papers only** - F tier only, avoid bloat
5. **Transparent scoring** - Keyword-based, no black-box AI ranking
6. **Natural backlog control** - Unscored articles reappear, no artificial caps
7. **Progressive enhancement** - Skeleton notes → user enriches over time
8. **Leverage existing tools** - Don't reinvent what Zotero/Obsidian do well

---

**Version:** 1.0  
**Status:** Design finalized, ready for implementation  
**Next Action:** Build Article Ranker module
