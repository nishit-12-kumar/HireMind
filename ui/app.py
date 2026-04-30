import streamlit as st
import sys
import os

# Ensure the root directory is in the path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline.orchestrator import hr_pipeline
from src.utils.pdf_reader import extract_text_from_pdf
from src.memory.chroma_store import save_candidates_to_memory
from ui.components.candidate_card import render_candidate_card
from src.utils.pdf_generator import generate_candidates_pdf

# --- NEW IMPORTS ---
from src.utils.logger import logger
from src.utils.exception import CustomException

# Log that the UI has initialized
logger.info("Starting HR Multi-Agent System Streamlit Dashboard...")

# --- Page Configuration ---
st.set_page_config(page_title="HR Multi-Agent Optimizer", page_icon="🤖", layout="wide")

st.title("HR Optimization with Multi-Agent System")
st.markdown("Automate early-stage recruitment with context-aware AI agents.")

# --- Initialize Session State ---
if 'final_state' not in st.session_state:
    st.session_state.final_state = None


# --- Sidebar Inputs ---
with st.sidebar:
    st.header("1. Job Setup")
    jd_text = st.text_area("Paste Job Description Here", height=300, key="jd_input_key")
    
    st.header("2. Candidate Resumes")
    uploaded_files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True, key="resume_upload_key")
    
    run_button = st.button("Run Pipeline", type="primary", use_container_width=True, key="run_pipeline_button")



# --- Main Dashboard Execution ---
if run_button:
    logger.info("User clicked 'Run Pipeline' button.")
    
    if not jd_text:
        logger.warning("Pipeline aborted: No Job Description provided.")
        st.error("Please paste a Job Description.")
    elif not uploaded_files:
        logger.warning("Pipeline aborted: No resumes uploaded.")
        st.error("Please upload at least one PDF resume.")
    else:
        with st.status("Processing Pipeline...", expanded=True) as status:
            try:
                # 1. Extract text from uploaded PDFs
                st.write("📄 Extracting text from PDFs...")
                logger.info(f"Initiating PDF extraction for {len(uploaded_files)} file(s).")
                resume_texts = [extract_text_from_pdf(pdf) for pdf in uploaded_files]
                
                # 2. Prepare the LangGraph State
                initial_state = {
                    "raw_jd": jd_text,
                    "resumes": resume_texts
                }
                
                # 3. Execute the Graph
                st.write("🤖 Agents are parsing, screening, matching, and generating questions...")
                logger.info("Invoking LangGraph pipeline from UI...")
                final_state = hr_pipeline.invoke(initial_state)
                
                # 4. Save to Memory
                st.write("💾 Saving evaluations to ChromaDB memory...")
                save_candidates_to_memory(
                    role_title=final_state["jd_schema"].role_title,
                    ranked_candidates=final_state["ranked_candidates"]
                )
                
                # Save the results to Streamlit's memory
                st.session_state.final_state = final_state
                
                status.update(label="Pipeline Complete!", state="complete", expanded=False)
                logger.info("Pipeline executed successfully and state saved to session.")
                
            except Exception as e:
                # Capture the detailed backend error for the log file
                detailed_error = CustomException(e, sys)
                logger.error(f"UI Pipeline Execution Failed: {str(detailed_error)}")
                
                # Show a safe, user-friendly error on the screen
                status.update(label="Pipeline Failed", state="error")
                st.error("An error occurred while processing the candidates. Please check the system logs.")
                st.error(f"Error details: {str(e)}")

# --- Render Results (Outside the Run Button block) ---
if st.session_state.final_state:
    try:
        final_state = st.session_state.final_state
        logger.info(f"Rendering UI dashboard for role: '{final_state['jd_schema'].role_title}'")
        
        st.success(f"Successfully processed candidates for the '{final_state['jd_schema'].role_title}' role.")
        
        # --- Generate and Download PDF Report ---
        st.write("---")
        pdf_bytes = generate_candidates_pdf(
            role_title=final_state["jd_schema"].role_title,
            ranked_candidates=final_state["ranked_candidates"],
            questions_map=final_state.get("interview_questions", {})
        )
        
        st.download_button(
            label="📥 Download Full HR Report (PDF)",
            data=pdf_bytes,
            file_name=f"HR_Report_{final_state['jd_schema'].role_title.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary"
        )
        st.write("---")
        
        # --- Interactive Filtering Controls ---
        st.header("Top Ranked Candidates")
        st.markdown("### Filter & Sort Results")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            min_score = st.slider("Minimum Match Score (%)", min_value=0, max_value=100, value=50, step=5)
        
        with filter_col2:
            max_exp_in_batch = max([c.profile.experience_years for c in final_state["ranked_candidates"]] + [1])
            min_exp = st.slider("Minimum Experience (Years)", min_value=0, max_value=int(max_exp_in_batch), value=0)
        
        with filter_col3:
            sort_option = st.selectbox(
                "Sort Candidates By", 
                options=["Match Score (High to Low)", "Experience (High to Low)", "Alphabetical (A-Z)"]
            )
        
        st.markdown("---") 
        
        # --- Apply Logic ---
        filtered_candidates = [
            c for c in final_state["ranked_candidates"]
            if c.match_score >= min_score and c.profile.experience_years >= min_exp
        ]
        
        if sort_option == "Match Score (High to Low)":
            filtered_candidates.sort(key=lambda x: x.match_score, reverse=True)
        elif sort_option == "Experience (High to Low)":
            filtered_candidates.sort(key=lambda x: x.profile.experience_years, reverse=True)
        elif sort_option == "Alphabetical (A-Z)":
            filtered_candidates.sort(key=lambda x: x.profile.name)
        
        # --- Render Results ---
        if not filtered_candidates:
            st.info("No candidates match your current filter criteria. Try lowering the thresholds.")
        else:
            for candidate in filtered_candidates:
                candidate_questions = final_state.get("interview_questions", {}).get(candidate.profile.name, {})
                render_candidate_card(candidate, candidate_questions)

    except Exception as e:
        detailed_error = CustomException(e, sys)
        logger.error(f"UI Dashboard Rendering Failed: {str(detailed_error)}")
        st.error("A critical error occurred while displaying the dashboard. Please refresh the page.")

elif not run_button:
    st.info("👈 Please enter a Job Description and upload resumes in the sidebar to begin.")

