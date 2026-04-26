from pydantic import BaseModel, Field
from typing import List

class CandidateProfile(BaseModel):
    name: str = Field(description="Full name of the candidate")
    skills: List[str] = Field(description="List of technical and soft skills possessed by the candidate")
    experience_years: int = Field(description="Total years of professional experience as an integer")
    education: str = Field(description="Highest educational qualification achieved")
    past_roles: List[str] = Field(description="List of previous job titles or roles held by the candidate")
    summary: str = Field(description="A brief professional summary of the candidate's background")


# Add this new class below CandidateProfile
class RankedCandidate(BaseModel):
    profile: CandidateProfile
    match_score: float = Field(description="Cosine similarity score between 0 and 100")