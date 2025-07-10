# Create app/utils/html_utils.py
import bleach

# Define allowed HTML tags for job descriptions
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'a', 'code', 'pre'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    '*': ['class']
}

def sanitize_html(html_content):
    """
    Sanitize HTML content to prevent XSS attacks while preserving formatting
    """
    if not html_content:
        return html_content
    
    return bleach.clean(
        html_content, 
        tags=ALLOWED_TAGS, 
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

def strip_html_tags(html_content):
    """
    Strip all HTML tags and return plain text
    """
    if not html_content:
        return html_content
    
    return bleach.clean(html_content, tags=[], strip=True)