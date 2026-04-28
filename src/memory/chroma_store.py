import chromadb
import os
import sys
from typing import List
from src.schemas.candidate_schema import RankedCandidate

# --- NEW IMPORTS ---
from src.utils.logger import logger
from src.utils.exception import CustomException

# Dynamically route to the artifacts folder at the root of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'artifacts', 'hr_memory')

def save_candidates_to_memory(role_title: str, ranked_candidates: List[RankedCandidate]):
    """
    Persists evaluated candidates and their scores to a local ChromaDB collection.
    """
    try:
        logger.info(f"Connecting to ChromaDB at path: {DB_PATH}")
        client = chromadb.PersistentClient(path=DB_PATH)
        
        # Get or create the collection for our talent pool
        logger.info("Accessing or creating collection: 'hr_talent_pool'")
        collection = client.get_or_create_collection(name="hr_talent_pool")
        
        logger.info(f"Preparing to save {len(ranked_candidates)} candidate(s) to memory for role '{role_title}'...")
        
        for idx, candidate in enumerate(ranked_candidates):
            # Generate a unique ID for the database
            safe_name = candidate.profile.name.replace(" ", "_").lower()
            safe_role = role_title.replace(" ", "_").lower()
            doc_id = f"{safe_role}_{safe_name}_{idx}"
            
            # We store the summary as the searchable document, and metadata for filtering
            collection.add(
                documents=[candidate.profile.summary],
                metadatas=[{
                    "name": candidate.profile.name,
                    "score": candidate.match_score,
                    "role_applied_for": role_title,
                    "experience_years": candidate.profile.experience_years
                }],
                ids=[doc_id]
            )
            
        logger.info(f"Successfully saved {len(ranked_candidates)} candidate(s) to ChromaDB memory.")
        return True
        
    except Exception as e:
        logger.error("Failed to save candidates to ChromaDB.")
        raise CustomException(e, sys)