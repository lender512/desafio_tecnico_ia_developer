"""
API Client for backend communication
"""
import requests
import streamlit as st
from typing import Dict, List, Optional, Any
from src.config.settings import API_BASE_URL


class APIClient:
    """API Client for backend communication"""
    
    @staticmethod
    def get(endpoint: str) -> Dict[str, Any]:
        """Make GET request to API"""
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return {}
    
    @staticmethod
    def get_file(endpoint: str) -> bytes:
        """Make GET request to download file"""
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            st.error(f"File Download Error: {str(e)}")
            return b""
    
    @staticmethod
    def post(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to API"""
        try:
            response = requests.post(
                f"{API_BASE_URL}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return {}
    
    @staticmethod
    def post_file(endpoint: str, data: Dict[str, Any]) -> bytes:
        """Make POST request to download file directly"""
        try:
            response = requests.post(
                f"{API_BASE_URL}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            st.error(f"File Generation Error: {str(e)}")
            return b""


def check_api_health() -> bool:
    """Check if API is available"""
    try:
        response = APIClient.get("/health")
        return response.get("status") == "healthy"
    except:
        return False


def load_customers() -> List[str]:
    """Load list of customer IDs"""
    response = APIClient.get("/customers")
    if response and "data" in response:
        return response["data"]
    return []


def load_customer_profile(customer_id: str) -> Optional[Dict]:
    """Load complete customer profile"""
    response = APIClient.get(f"/customers/{customer_id}/profile")
    if response and "data" in response:
        return response["data"]
    return None


def load_customer_summary(customer_id: str) -> Optional[Dict]:
    """Load customer summary"""
    response = APIClient.get(f"/customers/{customer_id}/summary")
    if response and "data" in response:
        return response["data"]
    return None


def perform_debt_analysis(customer_id: str, consolidation_offers: List[Dict] = None) -> Optional[Dict]:
    """Perform comprehensive debt analysis"""
    data = {
        "customer_id": customer_id,
        "consolidation_offers": consolidation_offers or [],
        "cure_dpd_first": True
    }
    response = APIClient.post("/analysis/debt-analysis", data)
    if response and "data" in response:
        return response["data"]
    return None


def simulate_payments(customer_id: str, strategy: str = "minimum") -> Optional[Dict]:
    """Simulate payment strategies"""
    endpoint = f"/analysis/simulate-{strategy}-payments"
    data = {
        "customer_id": customer_id,
        "cure_dpd_first": True
    }
    response = APIClient.post(endpoint, data)
    if response and "data" in response:
        return response["data"]
    return None


def get_eligible_offers(customer_id: str, offers: List[Dict], credit_score: int) -> Optional[Dict]:
    """Get eligible consolidation offers"""
    data = {
        "customer_id": customer_id,
        "offers": offers,
        "credit_score": credit_score
    }
    response = APIClient.post("/analysis/eligible-offers", data)
    if response and "data" in response:
        return response["data"]
    return None


def generate_pdf_report(customer_id: str, consolidation_offers: List[Dict] = None, report_title: str = "Report") -> Optional[Dict]:
    """Generate PDF report"""
    data = {
        "customer_id": customer_id,
        "include_consolidation": True,
        "consolidation_offers": consolidation_offers or [],
        "report_title": report_title
    }
    response = APIClient.post("/reports/generate-report", data)
    return response


def download_pdf_report(customer_id: str, filename: str) -> bytes:
    """Download PDF report file"""
    endpoint = f"/reports/download-report/{customer_id}/{filename}"
    return APIClient.get_file(endpoint)


def generate_and_download_pdf_report(customer_id: str, consolidation_offers: List[Dict] = None, report_title: str = None) -> bytes:
    """Generate and directly download PDF report"""
    data = {
        "customer_id": customer_id,
        "include_consolidation": True,
        "consolidation_offers": consolidation_offers or [],
        "report_title": report_title or f"Financial Analysis Report - {customer_id}"
    }
    return APIClient.post_file("/reports/generate-and-download", data)
