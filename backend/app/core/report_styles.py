"""CSS styles and HTML styling utilities for PDF reports."""


def get_professional_css_styles() -> str:
    """Get professional CSS styles for PDF reports."""
    return """
    <style>
    body {
        font-family: 'Arial', 'Helvetica', sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #fff;
    }
    
    h1 {
        color: #2c3e50;
        text-align: center;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        margin-bottom: 30px;
        font-size: 28px;
    }
    
    h2 {
        color: #34495e;
        border-left: 4px solid #3498db;
        padding-left: 15px;
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 22px;
    }
    
    h3 {
        color: #2c3e50;
        margin-top: 25px;
        margin-bottom: 10px;
        font-size: 18px;
    }
    
    p {
        margin-bottom: 15px;
        text-align: justify;
    }
    
    strong {
        color: #2c3e50;
        font-weight: bold;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    th {
        background-color: #3498db;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
    }
    
    td {
        padding: 10px 12px;
        border-bottom: 1px solid #ddd;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    tr:hover {
        background-color: #e8f4f8;
    }
    
    ul {
        padding-left: 20px;
    }
    
    li {
        margin-bottom: 8px;
    }
    
    .highlight {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 4px;
        padding: 15px;
        margin: 15px 0;
    }
    
    .savings {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 4px;
        padding: 15px;
        margin: 15px 0;
    }
    
    @media print {
        body {
            max-width: none;
            margin: 0;
            padding: 15px;
        }
        
        h1, h2, h3 {
            page-break-after: avoid;
        }
        
        table {
            page-break-inside: avoid;
        }
    }
    </style>
    """


def get_simple_css_styles() -> str:
    """Get simple CSS styles for fallback PDF generation."""
    return """
    <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { color: #333; text-align: center; }
    h2 { color: #555; border-bottom: 1px solid #ddd; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
    </style>
    """


def create_styled_html_document(html_content: str, title: str = "Financial Analysis Report") -> str:
    """
    Wrap HTML content in a complete HTML document with professional styling.
    
    Args:
        html_content: The body content HTML
        title: The document title
        
    Returns:
        Complete styled HTML document
    """
    css_styles = get_professional_css_styles()
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {css_styles}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """


def create_simple_html_document(html_content: str, title: str = "Financial Report") -> str:
    """
    Create a simple HTML document for fallback scenarios.
    
    Args:
        html_content: The body content HTML
        title: The document title
        
    Returns:
        Simple HTML document
    """
    css_styles = get_simple_css_styles()
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        {css_styles}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
