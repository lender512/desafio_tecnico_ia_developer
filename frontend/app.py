import streamlit as st

from src.config.settings import PAGE_CONFIG
from src.utils.api_client import check_api_health, load_customers, load_customer_profile, load_customer_summary
from src.utils.ui_helpers import get_custom_css, show_error_message, show_success_message
from src.pages.customer_dashboard import show_customer_dashboard
from src.pages.debt_analysis import show_debt_analysis
from src.pages.payment_simulations import show_payment_simulations
from src.pages.consolidation_analysis import show_consolidation_analysis
from src.pages.pdf_reports import show_pdf_reports
from src.pages.data_management import show_data_management


def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(**PAGE_CONFIG)


def apply_custom_styling():
    """Apply custom CSS styling"""
    st.markdown(get_custom_css(), unsafe_allow_html=True)


def render_header():
    """Render application header"""
    st.title("💰 Financial Restructuring Assistant")
    st.markdown("---")


def check_backend_health():
    """Check backend API health and display status"""
    if not check_api_health():
        show_error_message("Backend API is not available. Please ensure the backend is running on http://localhost:8000")
        st.stop()
    
    show_success_message("Backend API is healthy")


def render_sidebar():
    """Render sidebar navigation and customer selection"""
    st.sidebar.title("Navigation")
    
    # Load customers
    customers = load_customers()
    if not customers:
        show_error_message("No customers found in the system")
        st.stop()
    
    # Customer selection
    selected_customer = st.sidebar.selectbox(
        "Select Customer",
        customers,
        help="Choose a customer to analyze"
    )
    
    # Page selection
    page = st.sidebar.radio(
        "Select Page",
        [
            "Customer Dashboard",
            "Debt Analysis",
            "Payment Simulations", 
            "Consolidation Analysis",
            "PDF Reports",
            "Data Management"
        ]
    )
    
    return selected_customer, page


def load_customer_data(customer_id: str):
    """Load customer profile and summary data"""
    customer_profile = load_customer_profile(customer_id)
    customer_summary = load_customer_summary(customer_id)
    
    if not customer_profile or not customer_summary:
        show_error_message(f"Could not load data for customer {customer_id}")
        st.stop()
    
    return customer_profile, customer_summary


def route_to_page(page: str, customer_id: str, profile: dict, summary: dict):
    """Route to the selected page"""
    page_functions = {
        "Customer Dashboard": show_customer_dashboard,
        "Debt Analysis": show_debt_analysis,
        "Payment Simulations": show_payment_simulations,
        "Consolidation Analysis": show_consolidation_analysis,
        "PDF Reports": show_pdf_reports,
        "Data Management": show_data_management
    }
    
    page_function = page_functions.get(page)
    if page_function:
        page_function(customer_id, profile, summary)
    else:
        st.error(f"Unknown page: {page}")


def main():
    """Main application entry point"""
    # Setup
    setup_page_config()
    apply_custom_styling()
    
    # Header
    render_header()
    
    # Backend health check
    check_backend_health()
    
    # Sidebar navigation
    selected_customer, selected_page = render_sidebar()
    
    # Load customer data
    customer_profile, customer_summary = load_customer_data(selected_customer)
    
    # Route to selected page
    route_to_page(selected_page, selected_customer, customer_profile, customer_summary)


if __name__ == "__main__":
    main()
