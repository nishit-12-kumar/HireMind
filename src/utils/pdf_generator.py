import sys
from fpdf import FPDF

# --- NEW IMPORTS ---
from src.utils.logger import logger
from src.utils.exception import CustomException

def clean_text(text: str) -> str:
    """
    Cleans text to prevent PDF generation crashes from weird resume fonts or emojis.
    Converts unsupported characters into standard equivalents or question marks.
    """
    if not text:
        return ""
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_candidates_pdf(role_title: str, ranked_candidates: list, questions_map: dict) -> bytes:
    """
    Generates a multi-page PDF document. Each candidate gets their own page.
    """
    try:
        logger.info(f"Starting PDF report generation for role: '{role_title}'")
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        for candidate in ranked_candidates:
            logger.info(f"Adding PDF page for candidate: {candidate.profile.name}")
            
            # Add a fresh page for every single candidate
            pdf.add_page()
            
            # --- HEADER (Name and Score) ---
            pdf.set_font("Arial", 'B', 16)
            title = clean_text(f"{candidate.profile.name} - {candidate.match_score:.2f}% Match")
            pdf.cell(0, 10, title, ln=True, align='C')
            
            pdf.set_font("Arial", 'I', 12)
            pdf.cell(0, 10, clean_text(f"Applying for: {role_title}"), ln=True, align='C')
            pdf.ln(5)
            
            # --- CANDIDATE DETAILS ---
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "Background Overview", ln=True)
            pdf.set_font("Arial", '', 11)
            
            exp_edu = clean_text(f"Experience: {candidate.profile.experience_years} years | Education: {candidate.profile.education}")
            pdf.multi_cell(0, 6, exp_edu)
            
            skills = clean_text(f"Skills: {', '.join(candidate.profile.skills)}")
            pdf.multi_cell(0, 6, skills)
            pdf.ln(5)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "Professional Summary", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 6, clean_text(candidate.profile.summary))
            pdf.ln(8)
            
            # --- INTERVIEW QUESTIONS ---
            # Fetch the questions specific to this candidate
            questions = questions_map.get(candidate.profile.name, {})
            
            if questions:
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "Personalized Interview Questions", ln=True)
                
                # Technical
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 8, "Technical:", ln=True)
                pdf.set_font("Arial", '', 11)
                for q in questions.get("technical", []):
                    pdf.multi_cell(0, 6, clean_text(f"- {q}"))
                pdf.ln(3)
                
                # Behavioral
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 8, "Behavioral:", ln=True)
                pdf.set_font("Arial", '', 11)
                for q in questions.get("behavioral", []):
                    pdf.multi_cell(0, 6, clean_text(f"- {q}"))
                pdf.ln(3)
                
                # Role-Specific
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 8, "Role-Specific:", ln=True)
                pdf.set_font("Arial", '', 11)
                for q in questions.get("role_specific", []):
                    pdf.multi_cell(0, 6, clean_text(f"- {q}"))

        logger.info(f"Successfully generated PDF report with {len(ranked_candidates)} page(s).")
        
        # Return the generated PDF as raw bytes so Streamlit can download it
        return pdf.output(dest='S').encode('latin-1')

    except Exception as e:
        logger.error("Failed to generate PDF report.")
        raise CustomException(e, sys)






