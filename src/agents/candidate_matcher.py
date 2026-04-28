import sys
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from src.schemas.jd_schema import JDSchema
from src.schemas.candidate_schema import CandidateProfile, RankedCandidate

# --- NEW IMPORTS ---
from src.utils.logger import logger
from src.utils.exception import CustomException

# Load the embedding model globally so it doesn't reload for every resume
logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2) globally...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def match_candidates(jd: JDSchema, candidates: List[CandidateProfile]) -> List[RankedCandidate]:
    """
    Compares a list of candidate profiles against the JD and returns a ranked list with scores.
    """
    try:
        logger.info("Initializing candidate matching process...")
        
        # 1. Create a rich text representation of the Job Description using the correct exact variable
        jd_text = f"{jd.role_title} required skills: {' '.join(jd.required_skills)} preferred skills: {' '.join(jd.preferred_skills)} {jd.experience_years} years experience"
        jd_embedding = embedding_model.encode([jd_text])
        
        ranked_candidates = []
        
        logger.info(f"Scoring {len(candidates)} candidate(s) against the Job Description...")
        
        for candidate in candidates:
            # 2. Create a rich text representation of the Candidate
            candidate_text = f"{candidate.summary} skills: {' '.join(candidate.skills)} {candidate.experience_years} years experience"
            candidate_embedding = embedding_model.encode([candidate_text])
            
            # 3. Calculate cosine similarity and convert to a percentage
            score = cosine_similarity(jd_embedding, candidate_embedding)[0][0] * 100
            
            # 4. Store in our new RankedCandidate schema
            ranked_candidates.append(
                RankedCandidate(
                    profile=candidate,
                    match_score=round(score, 2)
                )
            )
            
        # 5. Sort the list from highest score to lowest
        ranked_candidates.sort(key=lambda x: x.match_score, reverse=True)
        
        logger.info("Candidate matching and ranking completed successfully.")
        return ranked_candidates

    except Exception as e:
        logger.error("Failed during the candidate matching and scoring process.")
        raise CustomException(e, sys)