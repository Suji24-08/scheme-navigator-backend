# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Settings:
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#     GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
#     LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
#     LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
#     LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "scheme-navigator")

#     # This is the important one for the next 2 days:
#     MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
#     LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# settings = Settings()

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "scheme-navigator")

    # This is the important one for the next 2 days:
    MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

settings = Settings()