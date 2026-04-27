import sys
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.config import llm
from src.schemas.jd_schema import JDSchema

# --- NEW IMPORTS ---
from src.utils.logger import logger
from src.utils.exception import CustomException

def parse_job_description(raw_jd: str) -> JDSchema:
    """
    Parses a raw job description string into a structured Pydantic schema.
    """
    try:
        logger.info("Initiating Job Description parsing...")
        
        parser = PydanticOutputParser(pydantic_object=JDSchema)
        
        prompt = PromptTemplate(
            template="""
            You are an expert HR recruiter. Extract the following information from the job description.
            \n{format_instructions}\n
            Job Description: {raw_jd}
            """,
            input_variables=["raw_jd"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        chain = prompt | llm | parser
        
        logger.info("Invoking LLM to extract Job Description details...")
        result = chain.invoke({"raw_jd": raw_jd})
        
        logger.info(f"Successfully parsed Job Description for role: '{result.role_title}'")
        return result
        
    except Exception as e:
        logger.error("Failed to parse Job Description.")
        # Pass the original error 'e' and the system context 'sys' to our custom handler
        raise CustomException(e, sys)