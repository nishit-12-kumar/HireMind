import sys
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.config import llm
from src.schemas.candidate_schema import CandidateProfile

# --- NEW IMPORTS ---
from src.utils.logger import logger
from src.utils.exception import CustomException

def screen_resume(resume_text: str) -> CandidateProfile:
    """
    Extracts structured information from a raw resume text.
    """
    try:
        # We only log a debug/info message here to avoid cluttering the log file 
        # too much if processing 100+ resumes.
        logger.info("Starting extraction for a candidate resume...")
        
        parser = PydanticOutputParser(pydantic_object=CandidateProfile)
        
        prompt = PromptTemplate(
            template="""
            You are an expert technical recruiter. Extract the following candidate details from the resume below.
            If any exact field is missing, infer it logically or leave it empty/0 as appropriate per the schema.
            \n{format_instructions}\n
            Resume Text: {resume_text}
            """,
            input_variables=["resume_text"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        chain = prompt | llm | parser
        
        result = chain.invoke({"resume_text": resume_text})
        
        logger.info(f"Successfully extracted profile for candidate: '{result.name}'")
        return result
        
    except Exception as e:
        logger.error("Failed to extract data from candidate resume.")
        raise CustomException(e, sys)