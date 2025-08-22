import os

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Page Configuration
PAGE_CONFIG = {
    "page_title": "Financial Restructuring Assistant",
    "page_icon": "💰",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}


# Sample Consolidation Offers
SAMPLE_CONSOLIDATION_OFFERS = [
    {
        "offer_id": "OF-CONSO-24M",
        "product_types_eligible": ["card", "personal"],
        "max_consolidated_balance": 50000,
        "new_rate_pct": 19.9,
        "max_term_months": 24,
        "conditions": "No mora >30 días al momento de la solicitud"
    },
    {
        "offer_id": "OF-CONSO-36M",
        "product_types_eligible": ["card", "personal", "micro"],
        "max_consolidated_balance": 75000,
        "new_rate_pct": 17.5,
        "max_term_months": 36,
        "conditions": "Score > 650 y sin mora activa"
    }
]
