# # import json
# # from app.core.config import settings

# # if not settings.MOCK_MODE:
# #     from langchain_openai import ChatOpenAI
# #     _llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0)
# # else:
# #     _llm = None


# import json
# from app.core.config import settings

# _llm = None
# if not settings.MOCK_MODE:
#     if settings.LLM_PROVIDER == "gemini":
#         from langchain_google_genai import ChatGoogleGenerativeAI
#         _llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             google_api_key=settings.GOOGLE_API_KEY,
#             temperature=0,
#         )
    
#     else:
#         from langchain_openai import ChatOpenAI
#         _llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0)

# def call_llm_json(prompt: str, mock_response: dict) -> dict:
#     """
#     Calls the LLM and expects a JSON object back.
#     In MOCK_MODE, returns mock_response untouched (no API call made).
#     Caller is responsible for providing a realistic mock_response per use site.
#     """
#     if settings.MOCK_MODE:
#         print("[llm_client] MOCK_MODE on — skipping real API call")
#         return mock_response

#     response = _llm.invoke(prompt)
#     text = response.content.strip()

#     # Defensive parsing — real LLM output isn't always clean JSON
#     if text.startswith("```"):
#         text = text.strip("`")
#         if text.startswith("json"):
#             text = text[4:]
#     try:
#         return json.loads(text)
#     except json.JSONDecodeError as e:
#         print(f"[llm_client] Failed to parse LLM output as JSON: {e}")
#         return {"error": "malformed_llm_output", "raw": text}
    
# def call_llm_text(prompt: str, mock_answer: str) -> str:
#     """
#     Calls the LLM and expects plain text back (not JSON).
#     In MOCK_MODE, returns mock_answer untouched (no API call made).
#     """
#     if settings.MOCK_MODE:
#         print("[llm_client] MOCK_MODE on — skipping real API call")
#         return mock_answer

#     response = _llm.invoke(prompt)
#     return response.content.strip()


import json
from app.core.config import settings

_llm = None
if not settings.MOCK_MODE:
    if settings.LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        _llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
        )
    elif settings.LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        _llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0,
        )
    else:
        from langchain_openai import ChatOpenAI
        _llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0)

def call_llm_json(prompt: str, mock_response: dict) -> dict:
    """
    Calls the LLM and expects a JSON object back.
    In MOCK_MODE, returns mock_response untouched (no API call made).
    Caller is responsible for providing a realistic mock_response per use site.
    """
    if settings.MOCK_MODE:
        print("[llm_client] MOCK_MODE on — skipping real API call")
        return mock_response

    response = _llm.invoke(prompt)
    text = response.content.strip()

    # Defensive parsing — real LLM output isn't always clean JSON
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[llm_client] Failed to parse LLM output as JSON: {e}")
        return {"error": "malformed_llm_output", "raw": text}
    
def call_llm_text(prompt: str, mock_answer: str) -> str:
    """
    Calls the LLM and expects plain text back (not JSON).
    In MOCK_MODE, returns mock_answer untouched (no API call made).
    """
    if settings.MOCK_MODE:
        print("[llm_client] MOCK_MODE on — skipping real API call")
        return mock_answer

    response = _llm.invoke(prompt)
    return response.content.strip()