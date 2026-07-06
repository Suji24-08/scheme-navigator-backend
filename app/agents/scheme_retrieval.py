# from app.core.vectorstore import retrieve_schemes
# from app.models.schemas import SchemeCandidate

# MIN_CANDIDATES_THRESHOLD = 2
# DISTANCE_GOOD_ENOUGH = 0.55


# def scheme_retrieval_node(state):
#     profile = state.profile

#     query_parts = []
#     if profile.occupation:
#         query_parts.append(profile.occupation)
#     if profile.is_student:
#         query_parts.append("student")
#     if profile.caste_category:
#         query_parts.append(profile.caste_category)
#     if profile.gender:
#         query_parts.append(profile.gender)
#     if profile.income_monthly is not None:
#         query_parts.append(f"monthly income {profile.income_monthly}")
#     if profile.income_annual is not None:
#         query_parts.append(f"annual income {profile.income_annual}")
#     if profile.state:
#         query_parts.append(profile.state)
#     if profile.disability_status:
#         query_parts.append("disability")

#     query_text = ", ".join(query_parts) if query_parts else state.raw_input

#     raw_results = retrieve_schemes(query_text, n_results=5)
#     attempt = 1

#     strong_matches = [r for r in raw_results if r["distance"] < DISTANCE_GOOD_ENOUGH]
#     if len(strong_matches) < MIN_CANDIDATES_THRESHOLD:
#         attempt = 2
#         refined_query = query_text + " scholarship eligibility criteria"
#         raw_results = retrieve_schemes(refined_query, n_results=5)

#     candidates = [
#         SchemeCandidate(
#             scheme_name=r["source"].replace(".txt", ""),
#             source_chunk=r["content"],
#             source_doc_id=r["source"],
#             similarity_score=round(1 - r["distance"], 4),
#         )
#         for r in raw_results
#     ]

#     state.audit_log.append({
#         "agent": "scheme_retrieval",
#         "query_used": query_text,
#         "attempts": attempt,
#         "candidates_returned": [c.source_doc_id for c in candidates],
#     })

#     return {
#         "candidates": candidates,
#         "retrieval_attempts": attempt,
#         "audit_log": state.audit_log,
#     }



from app.core.vectorstore import retrieve_schemes
from app.models.schemas import SchemeCandidate

MIN_CANDIDATES_THRESHOLD = 2
DISTANCE_GOOD_ENOUGH = 0.55


def scheme_retrieval_node(state):
    profile = state.profile

    query_parts = []
    if profile.occupation:
        query_parts.append(profile.occupation)
    if profile.is_student:
        query_parts.append("student")
    if profile.caste_category:
        query_parts.append(profile.caste_category)
    if profile.gender:
        query_parts.append(profile.gender)
    if profile.income_monthly is not None:
        query_parts.append(f"monthly income {profile.income_monthly}")
    if profile.income_annual is not None:
        query_parts.append(f"annual income {profile.income_annual}")
    if profile.state:
        query_parts.append(profile.state)
    if profile.disability_status:
        query_parts.append("disability")

    structured_text = ", ".join(query_parts) if query_parts else ""

    # Always blend in the raw input — structured fields alone drop domain-specific
    # terms (course type, institution type, e.g. "AICTE", "B.Tech", "engineering")
    # that matter a lot for semantic retrieval but aren't part of the fixed schema.
    query_text = f"{structured_text}. {state.raw_input}".strip(". ").strip()
    if not query_text:
        query_text = state.raw_input

    raw_results = retrieve_schemes(query_text, n_results=5)
    attempt = 1

    strong_matches = [r for r in raw_results if r["distance"] < DISTANCE_GOOD_ENOUGH]
    if len(strong_matches) < MIN_CANDIDATES_THRESHOLD:
        attempt = 2
        refined_query = query_text + " scholarship eligibility criteria"
        raw_results = retrieve_schemes(refined_query, n_results=5)

    candidates = [
        SchemeCandidate(
            scheme_name=r["source"].replace(".txt", ""),
            source_chunk=r["content"],
            source_doc_id=r["source"],
            similarity_score=round(1 - r["distance"], 4),
        )
        for r in raw_results
    ]

    state.audit_log.append({
        "agent": "scheme_retrieval",
        "query_used": query_text,
        "attempts": attempt,
        "candidates_returned": [c.source_doc_id for c in candidates],
    })

    return {
        "candidates": candidates,
        "retrieval_attempts": attempt,
        "audit_log": state.audit_log,
    }