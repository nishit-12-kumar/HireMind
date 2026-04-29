import sys
from langgraph.graph import StateGraph, END
from src.pipeline.state import HRState

# Import all agent logic
from src.agents.jd_parser import parse_job_description
from src.agents.resume_screener import screen_resume
from src.agents.candidate_matcher import match_candidates
from src.agents.interview_gen import generate_interview_questions

# --- NEW IMPORTS ---
from src.utils.logger import logger
from src.utils.exception import CustomException

# --- Node Definitions ---

def jd_parser_node(state: HRState):
    try:
        logger.info("--- ENTERING NODE: JD PARSER ---")
        parsed_jd = parse_job_description(state["raw_jd"])
        return {"jd_schema": parsed_jd}
    except Exception as e:
        logger.error("Pipeline crashed at JD Parser node.")
        raise CustomException(e, sys)

def resume_screener_node(state: HRState):
    try:
        logger.info("--- ENTERING NODE: RESUME SCREENER ---")
        logger.info(f"Processing batch of {len(state['resumes'])} resume(s)...")
        profiles = []
        for resume_text in state["resumes"]:
            profile = screen_resume(resume_text)
            profiles.append(profile)
        return {"candidate_profiles": profiles}
    except Exception as e:
        logger.error("Pipeline crashed at Resume Screener node.")
        raise CustomException(e, sys)

def candidate_matcher_node(state: HRState):
    try:
        logger.info("--- ENTERING NODE: CANDIDATE MATCHER ---")
        ranked = match_candidates(state["jd_schema"], state["candidate_profiles"])
        return {"ranked_candidates": ranked}
    except Exception as e:
        logger.error("Pipeline crashed at Candidate Matcher node.")
        raise CustomException(e, sys)

def interview_generator_node(state: HRState):
    try:
        logger.info("--- ENTERING NODE: INTERVIEW GENERATOR ---")
        # Generate questions only for the top 3 candidates to save time/tokens
        top_candidates = state["ranked_candidates"][:3]
        questions_map = {}
        
        for candidate in top_candidates:
            questions = generate_interview_questions(state["jd_schema"], candidate)
            questions_map[candidate.profile.name] = questions
            
        logger.info("Pipeline execution completed successfully.")
        return {"interview_questions": questions_map}
    except Exception as e:
        logger.error("Pipeline crashed at Interview Generator node.")
        raise CustomException(e, sys)


# --- Graph Construction ---
try:
    logger.info("Building and compiling LangGraph StateGraph...")
    
    # 1. Initialize the graph with our state schema
    graph = StateGraph(HRState)

    # 2. Add nodes
    graph.add_node('jd_parser', jd_parser_node)
    graph.add_node('resume_screener', resume_screener_node)
    graph.add_node('candidate_matcher', candidate_matcher_node)
    graph.add_node('interview_generator', interview_generator_node)

    # 3. Define the edges (the flow of execution)
    graph.add_edge('jd_parser', 'resume_screener')
    graph.add_edge('resume_screener', 'candidate_matcher')
    graph.add_edge('candidate_matcher', 'interview_generator')
    graph.add_edge('interview_generator', END)

    # 4. Set the starting point
    graph.set_entry_point('jd_parser')

    # 5. Compile the graph into an executable app
    hr_pipeline = graph.compile()
    
except Exception as e:
    logger.error("Failed to compile LangGraph pipeline.")
    raise CustomException(e, sys)