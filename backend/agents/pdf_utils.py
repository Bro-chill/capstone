# import PyPDF2
# import pdfplumber
# import re
# from typing import Optional

# # Constants
# MIN_TEXT_LENGTH = 100
# SCRIPT_INDICATORS = [
#     r'(INT\.|EXT\.)',
#     r'FADE IN:',
#     r'FADE OUT:',
#     r'[A-Z]{2,}\s*\n',
#     r'\([^)]+\)',
# ]
# MIN_SCRIPT_INDICATORS = 2

# def extract_text_from_pdf(pdf_file_path: str) -> str:
#     """Extract text from PDF using multiple methods for best results"""
    
#     # Try pdfplumber first (better for formatted text)
#     try:
#         text = extract_with_pdfplumber(pdf_file_path)
#         if _is_valid_extraction(text):
#             return clean_extracted_text(text)
#     except Exception as e:
#         print(f"⚠️ pdfplumber failed: {e}")
    
#     # Fallback to PyPDF2
#     try:
#         text = extract_with_pypdf2(pdf_file_path)
#         if _is_valid_extraction(text):
#             return clean_extracted_text(text)
#     except Exception as e:
#         print(f"⚠️ PyPDF2 failed: {e}")
    
#     raise ValueError("Could not extract readable text from PDF")

# def _is_valid_extraction(text: str) -> bool:
#     """Check if extracted text is valid"""
#     return text and len(text.strip()) > MIN_TEXT_LENGTH

# def extract_with_pdfplumber(pdf_path: str) -> str:
#     """Extract text using pdfplumber (better formatting preservation)"""
#     text_content = []
    
#     with pdfplumber.open(pdf_path) as pdf:
#         for page_num, page in enumerate(pdf.pages):
#             try:
#                 page_text = page.extract_text()
#                 if page_text:
#                     text_content.append(page_text)
#                     print(f"📄 Extracted page {page_num + 1}")
#             except Exception as e:
#                 print(f"⚠️ Error extracting page {page_num + 1}: {e}")
#                 continue
    
#     return "\n".join(text_content)

# def extract_with_pypdf2(pdf_path: str) -> str:
#     """Extract text using PyPDF2 (fallback method)"""
#     text_content = []
    
#     with open(pdf_path, 'rb') as file:
#         pdf_reader = PyPDF2.PdfReader(file)
        
#         for page_num, page in enumerate(pdf_reader.pages):
#             try:
#                 page_text = page.extract_text()
#                 if page_text:
#                     text_content.append(page_text)
#                     print(f"📄 Extracted page {page_num + 1}")
#             except Exception as e:
#                 print(f"⚠️ Error extracting page {page_num + 1}: {e}")
#                 continue
    
#     return "\n".join(text_content)

# def clean_extracted_text(text: str) -> str:
#     """Clean and normalize extracted text"""
#     # Remove excessive whitespace
#     text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
#     # Fix common PDF extraction issues
#     text = _fix_concatenated_lines(text)
#     text = _normalize_whitespace(text)
#     text = _preserve_script_formatting(text)
    
#     return text.strip()

# def _fix_concatenated_lines(text: str) -> str:
#     """Fix concatenated lines from PDF extraction"""
#     return re.sub(r'([a-z])([A-Z])', r'\1\n\2', text)

# def _normalize_whitespace(text: str) -> str:
#     """Normalize whitespace in text"""
#     text = re.sub(r'\s+', ' ', text)  # Normalize spaces
#     text = re.sub(r'\n ', '\n', text)  # Remove leading spaces after newlines
#     return text

# def _preserve_script_formatting(text: str) -> str:
#     """Preserve script formatting patterns"""
#     text = re.sub(r'(INT\.|EXT\.)', r'\n\1', text)  # Ensure scene headers on new lines
#     text = re.sub(r'(FADE IN:|FADE OUT:|CUT TO:)', r'\n\1', text)  # Preserve transitions
#     return text

# def validate_script_content(text: str) -> bool:
#     """Validate that extracted text looks like a script"""
#     matches = sum(1 for pattern in SCRIPT_INDICATORS 
#                  if re.search(pattern, text, re.IGNORECASE))
    
#     return matches >= MIN_SCRIPT_INDICATORS


import re
from typing import Optional

# Try to import PDF libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("Warning: PyPDF2 not available")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("Warning: pdfplumber not available")

# Constants
MIN_TEXT_LENGTH = 100
SCRIPT_INDICATORS = [
    r'(INT\.|EXT\.)',
    r'FADE IN:',
    r'FADE OUT:',
    r'[A-Z]{2,}\s*\n',
    r'\([^)]+\)',
]
MIN_SCRIPT_INDICATORS = 2

def extract_text_from_pdf(pdf_file_path: str) -> str:
    """Extract text from PDF using available methods"""
    
    if not PDFPLUMBER_AVAILABLE and not PYPDF2_AVAILABLE:
        raise ImportError(
            "No PDF processing libraries available. Please install: "
            "pip install pdfplumber PyPDF2"
        )
    
    # Try pdfplumber first (better for formatted text)
    if PDFPLUMBER_AVAILABLE:
        try:
            text = extract_with_pdfplumber(pdf_file_path)
            if _is_valid_extraction(text):
                return clean_extracted_text(text)
        except Exception as e:
            print(f"⚠️ pdfplumber failed: {e}")
    
    # Fallback to PyPDF2
    if PYPDF2_AVAILABLE:
        try:
            text = extract_with_pypdf2(pdf_file_path)
            if _is_valid_extraction(text):
                return clean_extracted_text(text)
        except Exception as e:
            print(f"⚠️ PyPDF2 failed: {e}")
    
    raise ValueError("Could not extract readable text from PDF")

def extract_with_pdfplumber(pdf_path: str) -> str:
    """Extract text using pdfplumber (better formatting preservation)"""
    if not PDFPLUMBER_AVAILABLE:
        raise ImportError("pdfplumber not available")
        
    text_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                    print(f"📄 Extracted page {page_num + 1}")
            except Exception as e:
                print(f"⚠️ Error extracting page {page_num + 1}: {e}")
                continue
    
    return "\n".join(text_content)

def extract_with_pypdf2(pdf_path: str) -> str:
    """Extract text using PyPDF2 (fallback method)"""
    if not PYPDF2_AVAILABLE:
        raise ImportError("PyPDF2 not available")
        
    text_content = []
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                    print(f"📄 Extracted page {page_num + 1}")
            except Exception as e:
                print(f"⚠️ Error extracting page {page_num + 1}: {e}")
                continue
    
    return "\n".join(text_content)

# Rest of your functions remain the same...
def _is_valid_extraction(text: str) -> bool:
    """Check if extracted text is valid"""
    return text and len(text.strip()) > MIN_TEXT_LENGTH

def clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted text"""
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    # Fix common PDF extraction issues
    text = _fix_concatenated_lines(text)
    text = _normalize_whitespace(text)
    text = _preserve_script_formatting(text)
    
    return text.strip()

def _fix_concatenated_lines(text: str) -> str:
    """Fix concatenated lines from PDF extraction"""
    return re.sub(r'([a-z])([A-Z])', r'\1\n\2', text)

def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text"""
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    text = re.sub(r'\n ', '\n', text)  # Remove leading spaces after newlines
    return text

def _preserve_script_formatting(text: str) -> str:
    """Preserve script formatting patterns"""
    text = re.sub(r'(INT\.|EXT\.)', r'\n\1', text)  # Ensure scene headers on new lines
    text = re.sub(r'(FADE IN:|FADE OUT:|CUT TO:)', r'\n\1', text)  # Preserve transitions
    return text

def validate_script_content(text: str) -> bool:
    """Validate that extracted text looks like a script"""
    matches = sum(1 for pattern in SCRIPT_INDICATORS 
                 if re.search(pattern, text, re.IGNORECASE))
    
    return matches >= MIN_SCRIPT_INDICATORS