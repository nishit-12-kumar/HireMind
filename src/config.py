# For Groq api

import os
from dotenv import load_dotenv

# # Option A: Groq API (Currently Active)
from langchain_groq import ChatGroq

# Load environment variables from the .env file
load_dotenv()

# Initialize the primary LLM
# The versatile 70B model is highly capable for strict JSON output tasks
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1, # Low temperature for more deterministic, structured outputs
    max_retries=3
)






# For gemini api

# import os
# from dotenv import load_dotenv

# # Option B: Google Gemini (New active provider)
# from langchain_google_genai import ChatGoogleGenerativeAI

# load_dotenv()

# # --- GEMINI CONFIG (Active) ---
# llm = ChatGoogleGenerativeAI(
#     # Updated to the newer, active model endpoint
#     model="gemini-2.5-flash", 
#     google_api_key=os.getenv("GEMINI_API_KEY"),
#     temperature=0.1,
#     max_retries=3
# )
