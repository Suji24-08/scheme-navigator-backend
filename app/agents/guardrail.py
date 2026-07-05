from app.core.llm_client import call_llm_json

PROMPT_TEMPLATE = """You are a guardrail for a government welfare scheme eligibility assistant.

Decide if this user message is asking about their eligibility for a government scheme, benefit, scholarship, subsidy, pension, or similar welfare program — OR is providing personal details (income, age, state, occupation, family, category) for that purpose.

Return ONLY a JSON object:
on_topic: true or false
reason: one short sentence

User message:
\"\"\"{text}\"\"\"

JSON:"""


def guardrail_node(state) -> dict:
    text_lower = state.raw_input.lower()

    # Mock heuristic: presence of scheme-related terms = on-topic
    scheme_keywords = [
        "income", "scheme", "eligib", "caste", "pension", "scholarship",
        "subsidy", "benefit", "state", "occupation", "age", "student",
        "disab", "family", "category", "sc", "st", "obc", "studying", "salary",
    ]
    mock_on_topic = any(kw in text_lower for kw in scheme_keywords)

    mock_response = {
        "on_topic": mock_on_topic,
        "reason": "Mentions personal/eligibility details." if mock_on_topic
                   else "No mention of schemes, benefits, or eligibility details.",
    }

    prompt = PROMPT_TEMPLATE.format(text=state.raw_input)
    result = call_llm_json(prompt, mock_response)

    on_topic = result.get("on_topic", True)  # fail open if parsing breaks — don't block real users on our own error
    reason = result.get("reason", "")

    state.audit_log.append({
        "agent": "guardrail",
        "on_topic": on_topic,
        "reason": reason,
    })

    if on_topic:
        return {"is_on_topic": True, "audit_log": state.audit_log}
    else:
        return {
            "is_on_topic": False,
            "refusal_message": "I can only help with questions about government scheme eligibility. Please describe your income, state, occupation, age, or family details so I can check what you may qualify for.",
            "audit_log": state.audit_log,
        }