from app.core.llm_client import call_llm_json
from app.models.schemas import GraphState, UserProfile

PROMPT_TEMPLATE = """Extract structured facts from this person's self-description for a government scheme eligibility check.

Return ONLY a JSON object with these keys (use null if not mentioned, don't guess):
income_monthly, income_annual, state, occupation, age, gender, family_size, caste_category, disability_status, is_student, ambiguous_fields (list of field names you're unsure about), extraction_notes (string, 1 sentence, or null).

Person's description:
\"\"\"{text}\"\"\"

JSON:"""


def profile_extraction_node(state: GraphState) -> dict:
    prompt = PROMPT_TEMPLATE.format(text=state.raw_input)

    # Realistic mock — simulates a genuinely ambiguous case, not a clean happy path
    # mock_response = {
    #     "income_monthly": 15000,
    #     "income_annual": None,
    #     "state": "Tamil Nadu",
    #     "occupation": "daily wage laborer",
    #     "age": 45,
    #     "gender": None,
    #     "family_size": 4,
    #     "caste_category": None,
    #     "disability_status": None,
    #     "is_student": False,
    #     "ambiguous_fields": ["caste_category", "gender"],
    #     "extraction_notes": "Caste category not mentioned; relevant for several scholarship/pension schemes."
    # }

    mock_response = _select_mock(state.raw_input)

    result = call_llm_json(prompt, mock_response)

    if result.get("error"):
        # Malformed output fallback: don't crash the graph, flag it in audit + proceed with empty profile
        profile = UserProfile(raw_text=state.raw_input, ambiguous_fields=["ALL"],
                               extraction_notes="LLM output could not be parsed; manual review needed.")
    else:
        profile = UserProfile(raw_text=state.raw_input, **{k: v for k, v in result.items() if k != "raw_text"})

    state.audit_log.append({
        "agent": "profile_extraction",
        "input": state.raw_input,
        "output": profile.model_dump(),
    })

    return {"profile": profile, "audit_log": state.audit_log}



MOCK_PROFILES = {
    "sc_eligible_student": {
        "income_monthly": None,
        "income_annual": 150000,
        "state": "Tamil Nadu",
        "occupation": None,
        "age": 15,
        "gender": "female",
        "family_size": 5,
        "caste_category": "SC",
        "disability_status": False,
        "is_student": True,
        "ambiguous_fields": [],
        "extraction_notes": None,
    },
    "not_student": {
        "income_monthly": 15000,
        "income_annual": None,
        "state": "Tamil Nadu",
        "occupation": "daily wage laborer",
        "age": 45,
        "gender": None,
        "family_size": 4,
        "caste_category": None,
        "disability_status": None,
        "is_student": False,
        "ambiguous_fields": ["caste_category", "gender"],
        "extraction_notes": "Caste category not mentioned; relevant for several scholarship/pension schemes.",
    },
}


def _select_mock(raw_input: str) -> dict:
    text = raw_input.lower()
    if "sc" in text or "scheduled caste" in text:
        return MOCK_PROFILES["sc_eligible_student"]
    return MOCK_PROFILES["not_student"]