# from app.core.llm_client import call_llm_json
# from app.models.schemas import EligibilityVerdict

# PROMPT_TEMPLATE = """You are checking whether a person is eligible for a government welfare scheme, based ONLY on the scheme's stated rules and the person's known facts. Do not assume anything not stated.

# SCHEME TEXT:
# \"\"\"{scheme_text}\"\"\"

# PERSON'S KNOWN FACTS:
# {profile_facts}

# PERSON'S UNCERTAIN/UNKNOWN FIELDS: {ambiguous_fields}

# Return ONLY a JSON object with these keys:
# verdict: one of "eligible", "not_eligible", "insufficient_evidence"
# matched_criteria: list of strings (criteria clearly satisfied)
# failed_criteria: list of strings (criteria clearly NOT satisfied)
# missing_info: list of strings (criteria that can't be checked because the person's facts don't cover it)
# citation: a short reference to the specific rule text this verdict rests on
# confidence: float between 0.0 and 1.0

# Rules:
# - If ANY required criterion is clearly failed, verdict must be "not_eligible", even if other criteria match.
# - If no criterion is clearly failed, but some required criteria can't be checked due to missing person facts, verdict must be "insufficient_evidence".
# - Only use "eligible" if every stated criterion is checked and satisfied.
# - Never guess a missing fact — treat it as missing_info instead.

# JSON:"""

# CASTE_PHRASE_MAP = {
#     "SC": ["scheduled caste"],
#     "ST": ["scheduled tribe"],
#     "OBC": ["other backward class", "obc"],
# }

# def _profile_facts_string(profile):
#     facts = []
#     for field in ["occupation", "is_student", "age", "gender", "caste_category",
#                   "income_monthly", "income_annual", "state", "disability_status", "family_size"]:
#         value = getattr(profile, field)
#         if value is not None:
#             facts.append(f"{field}: {value}")
#     return "\n".join(facts) if facts else "No facts extracted."


# def _build_mock_verdict(profile, candidate):
#     scheme_lower = candidate.source_chunk.lower()

#     requires_enrollment = any(
#         kw in scheme_lower for kw in ["class 9", "class 11", "undergraduate", "post-matric", "diploma"]
#     )
#     if profile.is_student is False and requires_enrollment:
#         return {
#             "verdict": "not_eligible",
#             "matched_criteria": [],
#             "failed_criteria": ["Applicant is not currently enrolled as a student, but this scheme requires active enrollment"],
#             "missing_info": [],
#             "citation": "Scheme requires current enrollment in a recognized course.",
#             "confidence": 0.85,
#         }

#     caste_restricted = any(kw in scheme_lower for kw in ["scheduled caste", "sc students", "obc", "minority"])
#     caste_unknown = "caste_category" in profile.ambiguous_fields or profile.caste_category is None

#     if caste_restricted and caste_unknown:
#         return {
#             "verdict": "insufficient_evidence",
#             "matched_criteria": [],
#             "failed_criteria": [],
#             "missing_info": ["caste_category was not stated by the user, and this scheme is restricted to a specific community"],
#             "citation": "Scheme is restricted to a specific caste/community category.",
#             "confidence": 0.4,
#         }

#     if caste_restricted and not caste_unknown:
#         relevant_phrases = CASTE_PHRASE_MAP.get(profile.caste_category, [])
#         category_matches = any(phrase in scheme_lower for phrase in relevant_phrases)

#         if category_matches:
#             return {
#                 "verdict": "eligible",
#                 "matched_criteria": [
#                     f"Belongs to {profile.caste_category} category, matching scheme requirement",
#                     "Currently enrolled as a student",
#                 ],
#                 "failed_criteria": [],
#                 "missing_info": [],
#                 "citation": "Scheme's stated category requirement matches applicant's category.",
#                 "confidence": 0.82,
#             }
#         return {
#             "verdict": "not_eligible",
#             "matched_criteria": [],
#             "failed_criteria": [f"Applicant's category ({profile.caste_category}) does not match this scheme's required category"],
#             "missing_info": [],
#             "citation": "Scheme is restricted to a category that does not match the applicant.",
#             "confidence": 0.8,
#         }

#     if profile.is_student:
#         return {
#             "verdict": "eligible",
#             "matched_criteria": ["Currently enrolled as a student", "No caste/community restriction applies"],
#             "failed_criteria": [],
#             "missing_info": [],
#             "citation": "General eligibility criteria appear satisfied based on available facts.",
#             "confidence": 0.75,
#         }

#     return {
#         "verdict": "insufficient_evidence",
#         "matched_criteria": [],
#         "failed_criteria": [],
#         "missing_info": ["Not enough profile information to confirm all stated criteria"],
#         "citation": "General eligibility criteria could not be fully verified from available facts.",
#         "confidence": 0.3,
#     }

# def eligibility_reasoning_node(state):
#     profile = state.profile
#     verdicts = []

#     for candidate in state.candidates:
#         prompt = PROMPT_TEMPLATE.format(
#             scheme_text=candidate.source_chunk,
#             profile_facts=_profile_facts_string(profile),
#             ambiguous_fields=profile.ambiguous_fields,
#         )
#         mock_response = _build_mock_verdict(profile, candidate)
#         result = call_llm_json(prompt, mock_response)

#         if result.get("error"):
#             verdict = EligibilityVerdict(
#                 scheme_name=candidate.scheme_name,
#                 verdict="insufficient_evidence",
#                 matched_criteria=[],
#                 failed_criteria=[],
#                 missing_info=["LLM output could not be parsed; manual review needed."],
#                 citation="N/A",
#                 confidence=0.0,
#             )
#         else:
#             verdict = EligibilityVerdict(
#                 scheme_name=candidate.scheme_name,
#                 verdict=result["verdict"],
#                 matched_criteria=result.get("matched_criteria", []),
#                 failed_criteria=result.get("failed_criteria", []),
#                 missing_info=result.get("missing_info", []),
#                 citation=result.get("citation", ""),
#                 confidence=result.get("confidence", 0.0),
#             )
#         verdicts.append(verdict)

#     state.audit_log.append({
#         "agent": "eligibility_reasoning",
#         "verdicts": [v.model_dump() for v in verdicts],
#     })

#     return {"verdicts": verdicts, "audit_log": state.audit_log}


from app.core.llm_client import call_llm_json
from app.models.schemas import EligibilityVerdict

BATCH_PROMPT_TEMPLATE = """You are checking whether a person is eligible for MULTIPLE government welfare schemes, based ONLY on each scheme's stated rules and the person's known facts. Do not assume anything not stated.

PERSON'S KNOWN FACTS:
{profile_facts}

PERSON'S UNCERTAIN/UNKNOWN FIELDS: {ambiguous_fields}

Below are {num_schemes} schemes to evaluate independently. Evaluate EACH one separately using only its own scheme text — do not let one scheme's rules affect another's verdict.

{schemes_block}

Return ONLY a JSON array with exactly {num_schemes} objects, in the SAME ORDER as the schemes above. Each object must have these keys:
scheme_name: the exact scheme name as given above
verdict: one of "eligible", "not_eligible", "insufficient_evidence"
matched_criteria: list of strings (criteria clearly satisfied)
failed_criteria: list of strings (criteria clearly NOT satisfied)
missing_info: list of strings (criteria that can't be checked because the person's facts don't cover it)
citation: a short reference to the specific rule text this verdict rests on
confidence: float between 0.0 and 1.0

Rules (apply independently per scheme):
- If ANY required criterion is clearly failed, verdict must be "not_eligible", even if other criteria match.
- If no criterion is clearly failed, but some required criteria can't be checked due to missing person facts, verdict must be "insufficient_evidence".
- Only use "eligible" if every stated criterion is checked and satisfied.
- Never guess a missing fact — treat it as missing_info instead.

JSON array:"""

CASTE_PHRASE_MAP = {
    "SC": ["scheduled caste"],
    "ST": ["scheduled tribe"],
    "OBC": ["other backward class", "obc"],
}

def _profile_facts_string(profile):
    facts = []
    for field in ["occupation", "is_student", "age", "gender", "caste_category",
                  "income_monthly", "income_annual", "state", "disability_status", "family_size"]:
        value = getattr(profile, field)
        if value is not None:
            facts.append(f"{field}: {value}")
    return "\n".join(facts) if facts else "No facts extracted."


def _build_mock_verdict(profile, candidate):
    scheme_lower = candidate.source_chunk.lower()

    requires_enrollment = any(
        kw in scheme_lower for kw in ["class 9", "class 11", "undergraduate", "post-matric", "diploma"]
    )
    if profile.is_student is False and requires_enrollment:
        return {
            "scheme_name": candidate.scheme_name,
            "verdict": "not_eligible",
            "matched_criteria": [],
            "failed_criteria": ["Applicant is not currently enrolled as a student, but this scheme requires active enrollment"],
            "missing_info": [],
            "citation": "Scheme requires current enrollment in a recognized course.",
            "confidence": 0.85,
        }

    caste_restricted = any(kw in scheme_lower for kw in ["scheduled caste", "sc students", "obc", "minority"])
    caste_unknown = "caste_category" in profile.ambiguous_fields or profile.caste_category is None

    if caste_restricted and caste_unknown:
        return {
            "scheme_name": candidate.scheme_name,
            "verdict": "insufficient_evidence",
            "matched_criteria": [],
            "failed_criteria": [],
            "missing_info": ["caste_category was not stated by the user, and this scheme is restricted to a specific community"],
            "citation": "Scheme is restricted to a specific caste/community category.",
            "confidence": 0.4,
        }

    if caste_restricted and not caste_unknown:
        relevant_phrases = CASTE_PHRASE_MAP.get(profile.caste_category, [])
        category_matches = any(phrase in scheme_lower for phrase in relevant_phrases)

        if category_matches:
            return {
                "scheme_name": candidate.scheme_name,
                "verdict": "eligible",
                "matched_criteria": [
                    f"Belongs to {profile.caste_category} category, matching scheme requirement",
                    "Currently enrolled as a student",
                ],
                "failed_criteria": [],
                "missing_info": [],
                "citation": "Scheme's stated category requirement matches applicant's category.",
                "confidence": 0.82,
            }
        return {
            "scheme_name": candidate.scheme_name,
            "verdict": "not_eligible",
            "matched_criteria": [],
            "failed_criteria": [f"Applicant's category ({profile.caste_category}) does not match this scheme's required category"],
            "missing_info": [],
            "citation": "Scheme is restricted to a category that does not match the applicant.",
            "confidence": 0.8,
        }

    if profile.is_student:
        return {
            "scheme_name": candidate.scheme_name,
            "verdict": "eligible",
            "matched_criteria": ["Currently enrolled as a student", "No caste/community restriction applies"],
            "failed_criteria": [],
            "missing_info": [],
            "citation": "General eligibility criteria appear satisfied based on available facts.",
            "confidence": 0.75,
        }

    return {
        "scheme_name": candidate.scheme_name,
        "verdict": "insufficient_evidence",
        "matched_criteria": [],
        "failed_criteria": [],
        "missing_info": ["Not enough profile information to confirm all stated criteria"],
        "citation": "General eligibility criteria could not be fully verified from available facts.",
        "confidence": 0.3,
    }


def _fallback_verdict(candidate, reason):
    return EligibilityVerdict(
        scheme_name=candidate.scheme_name,
        verdict="insufficient_evidence",
        matched_criteria=[],
        failed_criteria=[],
        missing_info=[reason],
        citation="N/A",
        confidence=0.0,
    )


def eligibility_reasoning_node(state):
    profile = state.profile
    candidates = state.candidates

    if not candidates:
        state.audit_log.append({"agent": "eligibility_reasoning", "verdicts": []})
        return {"verdicts": [], "audit_log": state.audit_log}

    schemes_block = "\n\n".join(
        f"--- SCHEME {i+1}: {c.scheme_name} ---\n{c.source_chunk}"
        for i, c in enumerate(candidates)
    )

    prompt = BATCH_PROMPT_TEMPLATE.format(
        profile_facts=_profile_facts_string(profile),
        ambiguous_fields=profile.ambiguous_fields,
        num_schemes=len(candidates),
        schemes_block=schemes_block,
    )

    mock_response = [_build_mock_verdict(profile, c) for c in candidates]

    result = call_llm_json(prompt, mock_response)

    verdicts = []

    if isinstance(result, dict) and result.get("error"):
        # Whole batch failed to parse — fall back for every candidate
        for candidate in candidates:
            verdicts.append(_fallback_verdict(candidate, "LLM output could not be parsed; manual review needed."))
    elif isinstance(result, list):
        for i, candidate in enumerate(candidates):
            if i < len(result) and isinstance(result[i], dict):
                item = result[i]
                verdicts.append(EligibilityVerdict(
                    scheme_name=candidate.scheme_name,
                    verdict=item.get("verdict", "insufficient_evidence"),
                    matched_criteria=item.get("matched_criteria", []),
                    failed_criteria=item.get("failed_criteria", []),
                    missing_info=item.get("missing_info", []),
                    citation=item.get("citation", ""),
                    confidence=item.get("confidence", 0.0),
                ))
            else:
                # Array shorter than expected, or malformed entry — fail safe for this scheme only
                verdicts.append(_fallback_verdict(candidate, "LLM did not return a verdict for this scheme; manual review needed."))
    else:
        # Unexpected shape (e.g. LLM returned a single object, not an array)
        for candidate in candidates:
            verdicts.append(_fallback_verdict(candidate, "LLM output was not in the expected array format; manual review needed."))

    state.audit_log.append({
        "agent": "eligibility_reasoning",
        "verdicts": [v.model_dump() for v in verdicts],
    })

    return {"verdicts": verdicts, "audit_log": state.audit_log}