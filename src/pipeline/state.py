from typing import TypedDict, List, Dict, Any
from src.schemas.jd_schema import JDSchema
from src.schemas.candidate_schema import CandidateProfile, RankedCandidate

class HRState(TypedDict):
    # Input from UI
    raw_jd: str
    resumes: List[str] # List of raw text extracted from multiple PDFs
    
    # Output of Agent 1
    jd_schema: JDSchema
    
    # Output of Agent 2
    candidate_profiles: List[CandidateProfile]
    
    # Output of Agent 3
    ranked_candidates: List[RankedCandidate]
    
    # Output of Agent 4 (Maps candidate name to their question dictionary)
    interview_questions: Dict[str, dict]