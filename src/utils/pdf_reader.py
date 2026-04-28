import sys
import pdfplumber

# --- NEW IMPORTS ---
from src.utils.logger import logger
from src.utils.exception import CustomException

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts all text from an uploaded PDF file using pdfplumber.
    """
    try:
        # Streamlit uploaded files have a .name attribute we can log
        file_name = pdf_file.name if hasattr(pdf_file, 'name') else "Unknown_PDF"
        logger.info(f"Extracting text from document: {file_name}")
        
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
        # Check if the PDF was just images (no readable text)
        if not text.strip():
            logger.warning(f"Extracted 0 characters from {file_name}. This might be a scanned image or protected PDF.")
        else:
            logger.info(f"Successfully extracted {len(text)} characters from {file_name}.")
            
        return text
        
    except Exception as e:
        file_name = pdf_file.name if hasattr(pdf_file, 'name') else "Unknown_PDF"
        logger.error(f"Failed to read or extract text from PDF: {file_name}")
        raise CustomException(e, sys)