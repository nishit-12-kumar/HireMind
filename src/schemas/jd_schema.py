from pydantic import BaseModel, Field
from typing import List

class JDSchema(BaseModel):
    role_title: str = Field(description="The title of the job role")
    required_skills: List[str] = Field(description="List of mandatory skills required for the job")
    preferred_skills: List[str] = Field(description="List of nice-to-have or preferred skills")
    experience_years: int = Field(description="Minimum years of experience required as an integer")
    education: str = Field(description="Educational qualifications required")
    responsibilities: List[str] = Field(description="List of key responsibilities for the role")
    role_type: str = Field(description="Type of role (e.g., Full-time, Contract, Hybrid, Remote)")