from app.core.llm_client import call_llm_json
from app.models.schemas import FinalExplanation

CONFIDENCE_THRESHOLD = 0.7

PROMPT_TEMPLATE = """Write a short, plain-language explanation (2-3 sentences, no jargon) for a citizen about their eligibility for this scheme, based on the verdict below. Always end with the citation naturally worked into the sentence, not as a separate label.

Scheme: {scheme_name}
Verdict: {verdict}
Matched criteria: {matched}
Failed criteria: {failed}
Missing info: {missing}
Citation: {citation}

Return ONLY a JSON object with one key: "summary" (the plain-language text).

JSON:"""


def _route(verdict_obj):
    if verdict_obj.verdict == "not_eligible":
        return "not_shown"
    if verdict_obj.verdict == "eligible" and verdict_obj.confidence >= CONFIDENCE_THRESHOLD:
        return "confirmed_match"
    return "verify_with_local_office"


def _build_mock_summary(verdict_obj, show_as):
    if show_as == "not_shown":
        return {"summary": "Not eligible based on stated criteria."}
    if show_as == "confirmed_match":
        return {"summary": f"You appear to qualify for {verdict_obj.scheme_name}, based on {verdict_obj.citation}"}
    return {
        "summary": (
            f"We couldn't fully confirm your eligibility for {verdict_obj.scheme_name} — "
            f"{', '.join(verdict_obj.missing_info) if verdict_obj.missing_info else 'some details are unclear'}. "
            f"Please verify with your local office. Reference: {verdict_obj.citation}"
        )
    }


def explainer_router_node(state):
    final_results = []

    for verdict_obj in state.verdicts:
        show_as = _route(verdict_obj)

        if show_as == "not_shown":
            continue  # don't bother generating explanation text for rejected schemes

        prompt = PROMPT_TEMPLATE.format(
            scheme_name=verdict_obj.scheme_name,
            verdict=verdict_obj.verdict,
            matched=verdict_obj.matched_criteria,
            failed=verdict_obj.failed_criteria,
            missing=verdict_obj.missing_info,
            citation=verdict_obj.citation,
        )
        mock_response = _build_mock_summary(verdict_obj, show_as)
        result = call_llm_json(prompt, mock_response)

        summary = result.get("summary", "Unable to generate explanation.")

        final_results.append(FinalExplanation(
            scheme_name=verdict_obj.scheme_name,
            show_as=show_as,
            plain_language_summary=summary,
            citation=verdict_obj.citation,
            confidence=verdict_obj.confidence,
        ))

    state.audit_log.append({
        "agent": "explainer_router",
        "final_results": [r.model_dump() for r in final_results],
    })

    return {"final_results": final_results, "audit_log": state.audit_log}