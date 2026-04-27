import sys
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from src.config import llm
from src.schemas.jd_schema import JDSchema
from src.schemas.candidate_schema import RankedCandidate

# --- NEW IMPORTS ---
from src.utils.logger import logger
from src.utils.exception import CustomException

class InterviewQuestionSet(BaseModel):
    technical: List[str] = Field(description="2 technical questions based on candidate skills vs job requirements")
    behavioral: List[str] = Field(description="2 behavioral questions")
    role_specific: List[str] = Field(description="2 role-specific questions")

def generate_interview_questions(jd: JDSchema, candidate: RankedCandidate) -> dict:
    """
    Generates personalized interview questions for a candidate based on the JD.
    """
    try:
        logger.info(f"Generating interview questions for candidate: '{candidate.profile.name}'...")
        
        parser = PydanticOutputParser(pydantic_object=InterviewQuestionSet)
        
        prompt = PromptTemplate(
            template="""
            You are an expert technical interviewer.
            Generate 6 interview questions for {candidate_name}.
            
            Job requires: {jd_skills}
            Candidate has: {candidate_skills}
            
            Target real gaps or strengths based on the comparison above.
            
            {format_instructions}
            """,
            input_variables=["candidate_name", "jd_skills", "candidate_skills"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        chain = prompt | llm | parser
        
        result = chain.invoke({
            "candidate_name": candidate.profile.name,
            "jd_skills": ", ".join(jd.required_skills),
            "candidate_skills": ", ".join(candidate.profile.skills)
        })
        
        logger.info(f"Successfully generated interview questions for '{candidate.profile.name}'")
        return result.model_dump()

    except Exception as e:
        logger.error(f"Failed to generate interview questions for '{candidate.profile.name}'.")
        raise CustomException(e, sys)