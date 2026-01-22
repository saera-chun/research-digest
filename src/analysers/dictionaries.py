"""
Keyword dictionaries for metadata extraction (geography, methods, stakeholders).

- Canonical keys map to lists of aliases/synonyms to match in text.
- Keep lists lowercase; matching code will normalize input texts accordingly.

Update and extend these lists as you encounter new terms in your feed output.
"""

from typing import Dict, List

# Geography: NZ-centric with common international fallbacks
GEOGRAPHY_KEYWORDS: Dict[str, List[str]] = {
    # --- Tier 1: Urban Growth Partnerships / High policy relevance ---
    "Auckland": ["auckland", "tāmaki makaurau", "tamaki makaurau", "waitematā", "waitemata"],
    "Wellington": ["wellington", "te whanganui-a-tara", "hutt valley", "lower hutt", "upper hutt", "porirua", "kapiti"],
    "Christchurch": ["christchurch", "ōtautahi", "otautahi", "greater christchurch", "canterbury"],
    "Tauranga": ["tauranga", "western bay of plenty", "mount maunganui", "bay of plenty"],
    "Hamilton-Waikato": ["hamilton", "kirikiriroa", "waikato", "future proof"],
    "Queenstown Lakes": ["queenstown", "queenstown lakes", "wanaka", "central otago"],

    # --- Priority Areas: deprivation & emergency housing focus ---
    "Rotorua": ["rotorua", "te arawa"],
    "Hawke's Bay": ["hawkes bay", "hawke's bay", "napier", "hastings", "te matau-a-māui"],
    "Northland": ["northland", "tai tokerau", "whangarei", "far north"],
    "Gisborne": ["gisborne", "tairāwhiti", "tairawhiti", "east coast"],

    # --- National scale ---
    "New Zealand": ["new zealand", "aotearoa", "nz"],

    # --- International comparators (Anglosphere / Reform / Alternative-model / Theory origins)
    "Australia": ["australia", "sydney", "melbourne", "brisbane", "victoria", "nsw"],
    "United Kingdom": ["united kingdom", "uk", "london", "england", "scotland"],
    "Canada": ["canada", "vancouver", "toronto", "british columbia"],
    "Ireland": ["ireland", "dublin"],

    # Reform / zoning hotspots
    "Minneapolis": ["minneapolis"],
    "California": ["california", "san francisco", "los angeles", "bay area", "sf bay area"],
    "Oregon": ["oregon", "portland", "portland, oregon"],

    # Alternative model / social housing examples
    "Vienna": ["vienna", "wien"],
    "Berlin": ["berlin"],
    "Germany": ["germany", "deutschland"],
    "Singapore": ["singapore"],
    "Sweden": ["sweden", "stockholm"],
    "Denmark": ["denmark", "copenhagen"],
    "Finland": ["finland", "helsinki"],

    # Theory / continental context
    "France": ["france", "paris"],
}

# Note: policy-focused terms intentionally omitted from geography keywords to avoid false positives

# Methods: common qualitative, quantitative and spatial methods
METHOD_KEYWORDS: Dict[str, List[str]] = {
    # --- PhD Core: Phenomenology & Spatial Theory ---
    "phenomenology-neo": ["hermann schmitz", "new phenomenology", "neo-phenomenology", "felt body", "corporeal", "leib", "situational atmosphere"],
    "phenomenology-general": ["phenomenology", "phenomenological", "lived experience", "embodiment", "merleau-ponty"],
    "counter-mapping": ["counter-mapping", "counter mapping", "deep mapping", "critical gis", "qualitative gis"],
    "spatial-justice": ["spatial justice", "right to the city", "socio-spatial"],

    # --- NZ Specific: Indigenous & Pacific Methodologies ---
    "kaupapa-maori": ["kaupapa maori", "kaupapa māori", "mātauranga", "whakapapa", "mana whenua"],
    "talanoa": ["talanoa", "pacific methodology", "pasifika methodology"],
    
    # --- Policy Core: Quantitative & Administrative Data ---
    "administrative-data": ["idi", "integrated data infrastructure", "admin data", "tax data", "census"],
    "spatial-analysis": ["spatial analysis", "gis", "geospatial", "remote sensing", "catchment analysis"],
    "econometrics": ["econometric", "regression", "difference-in-differences", "hedonic", "causal inference"],
    "survey-data": ["survey", "questionnaire", "cross-sectional", "household economic survey", "hes"],

    # --- General Academic Standards ---
    "mixed-methods": ["mixed methods", "mixed-methods", "triangulation"],
    "ethnography": ["ethnography", "ethnographic", "participant observation", "fieldwork"],
    "qualitative-general": ["qualitative", "semi-structured interview", "focus group", "thematic analysis", "content analysis"],
    "case-study": ["case study", "case-study", "multiple case studies"],
    "systematic-review": ["systematic review", "meta-analysis", "literature review", "scoping review"]
}

# Stakeholders: people, organisations, and institutions relevant to housing/policy
STAKEHOLDER_KEYWORDS: Dict[str, List[str]] = {
    "renters": ["tenant", "tenants", "renter", "renters", "rental"],
    "homeowners": ["homeowner", "homeowners", "owner-occupier", "owner occupier"],
    "landlords": ["landlord", "landlords", "private landlord"],
    "developers": ["developer", "developers", "housebuilder", "property developer"],
    "local-government": ["council", "local authority", "municipality", "city council"],
    "national-government": ["central government", "national government", "ministry", "federal government"],
    "planners": ["urban planner", "planning authority", "planner", "zoning"],
    "community-groups": ["community organisation", "community organization", "advocacy group", "resident association"],
    "housing-associations": ["housing association", "social housing", "public housing"],
    "kainga-ora": ["kainga ora", "kainga-ora", "kaingā ora"],
    "private-sector": ["private sector", "commercial", "market"],
    "public-sector": ["public sector", "state", "government intervention"],
    "non-profit": ["non-profit", "non profit", "ngo", "charity"]
}

__all__ = [
    "GEOGRAPHY_KEYWORDS",
    "METHOD_KEYWORDS",
    "STAKEHOLDER_KEYWORDS",
]
