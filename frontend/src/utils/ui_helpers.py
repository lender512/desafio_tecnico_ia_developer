"""
UI Helper functions and components
"""
import streamlit as st
from typing import Dict, Any


def safe_numeric_parse(value: Any, default: float = 0.0) -> float:
    """Safely parse a value to float"""
    if value is None:
        return default
    
    try:
        # Handle string representations
        if isinstance(value, str):
            # Remove common currency symbols and whitespace
            cleaned = value.replace('$', '').replace(',', '').strip()
            if cleaned == '' or cleaned.lower() in ['n/a', 'na', 'null', 'none']:
                return default
            return float(cleaned)
        
        # Handle numeric types
        elif isinstance(value, (int, float)):
            return float(value)
        
        # Handle other types
        else:
            return float(value)
            
    except (ValueError, TypeError):
        return default


def safe_int_parse(value: Any, default: int = 0) -> int:
    """Safely parse a value to int"""
    try:
        parsed_float = safe_numeric_parse(value, default)
        return int(parsed_float)
    except (ValueError, TypeError):
        return default


def get_risk_indicator(risk_level: str) -> str:
    """Get risk level indicator emoji"""
    risk_indicators = {
        "low": "🟢",
        "medium": "🟡", 
        "high": "🔴"
    }
    return risk_indicators.get(risk_level.lower(), "⚪")


def format_currency(amount: float | str) -> str:
    """Format amount as currency"""
    if isinstance(amount, float):
        return f"${amount:,.2f}"
    return f"${float(amount):,.2f}"


def format_percentage(percentage: float) -> str:
    """Format number as percentage"""
    return f"{percentage:.1f}%"


def display_metric_card(title: str, value: str, delta: str = None, card_type: str = "normal"):
    """Display a styled metric card"""
    css_class = {
        "normal": "metric-card",
        "success": "metric-card success-metric",
        "warning": "metric-card warning-metric", 
        "danger": "metric-card danger-metric",
        "info": "metric-card info-metric"
    }.get(card_type, "metric-card")
    
    st.markdown(f"""
    <div class="{css_class}">
        <h4>{title}</h4>
        <h2>{value}</h2>
        {f'<p>{delta}</p>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)


def show_loading_spinner(message: str = "Loading..."):
    """Show loading spinner with message"""
    return st.spinner(message)


def show_success_message(message: str):
    """Show success message"""
    st.success(f"✅ {message}")


def show_error_message(message: str):
    """Show error message"""
    st.error(f"❌ {message}")


def show_warning_message(message: str):
    """Show warning message"""
    st.warning(f"⚠️ {message}")


def show_info_message(message: str):
    """Show info message"""
    st.info(f"💡 {message}")


def create_two_column_layout():
    """Create two column layout"""
    return st.columns(2)


def create_three_column_layout():
    """Create three column layout"""
    return st.columns(3)


def create_four_column_layout():
    """Create four column layout"""
    return st.columns(4)


def display_data_table(data, title: str = None):
    """Display data as formatted table"""
    if title:
        st.subheader(title)
    
    if data:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No data available")


def create_expandable_section(title: str, content_func, expanded: bool = False):
    """Create expandable section"""
    with st.expander(title, expanded=expanded):
        content_func()


def display_consolidation_offer(offer: Dict[str, Any]):
    """Display a consolidation offer in a formatted way"""
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Offer ID", offer["offer_id"])
            st.metric("Rate", f"{offer['new_rate_pct']}%")
        
        with col2:
            st.metric("Max Term", f"{offer['max_term_months']} months")
            st.metric("Max Balance", format_currency(offer['max_consolidated_balance']))
        
        with col3:
            st.write("**Eligible Products:**")
            for product in offer["product_types_eligible"]:
                st.write(f"• {product}")
        
        st.write(f"**Conditions:** {offer['conditions']}")
        st.markdown("---")


def render_customer_header(customer_id: str, profile: Dict[str, Any]):
    """Render customer information header"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Customer ID", customer_id)
    
    with col2:
        if 'credit_score' in profile:
            score = profile['credit_score']
            if score >= 750:
                score_color = "🟢"
            elif score >= 650:
                score_color = "🟡"
            else:
                score_color = "🔴"
            st.metric("Credit Score", f"{score_color} {score}")
        else:
            st.metric("Credit Score", "N/A")
    
    with col3:
        if 'total_debt' in profile:
            st.metric("Total Debt", format_currency(profile['total_debt']))
        else:
            st.metric("Total Debt", "N/A")
    
    with col4:
        if 'monthly_income' in profile:
            st.metric("Monthly Income", format_currency(profile['monthly_income']))
        else:
            st.metric("Monthly Income", "N/A")


def get_custom_css() -> str:
    """Get custom CSS styles"""
    return """
    <style>
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .success-metric {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }
        .warning-metric {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
        }
        .danger-metric {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        .info-metric {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
        }
        .stButton > button {
            width: 100%;
        }
        .metric-container {
            background-color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            margin: 0.5rem 0;
        }
    </style>
    """
