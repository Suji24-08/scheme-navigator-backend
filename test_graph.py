# # from app.core.graph import build_graph

# # def run_test():
# #     graph = build_graph()

# #     initial_state = {
# #         "raw_input": "I am a girl studying in class 10, my family income is 1.5 lakh per year",
# #         "user_profile": {},
# #         "scheme_candidates": [],
# #         "audit_log": [],
# #     }

# #     final_state = graph.invoke(initial_state)

# #     print("\n=== USER PROFILE (from Agent 1) ===")
# #     print(final_state.get("user_profile"))

# #     print("\n=== SCHEME CANDIDATES (from Agent 2) ===")
# #     for c in final_state.get("scheme_candidates", []):
# #         print(f"- {c['source']}  (distance: {c['distance']:.4f})")

# #     print("\n=== AUDIT LOG ===")
# #     for entry in final_state.get("audit_log", []):
# #         print(entry)

# # if __name__ == "__main__":
# #     run_test()

# from app.core.graph import build_graph

# def run_test():
#     graph = build_graph()

#     initial_state = {
#         "raw_input": "I am a girl studying in class 10, my family income is 1.5 lakh per year",
#         "audit_log": [],
#     }

#     final_state = graph.invoke(initial_state)

#     print("\n=== USER PROFILE (from Agent 1) ===")
#     print(final_state.get("profile"))

#     print("\n=== SCHEME CANDIDATES (from Agent 2) ===")
#     for c in final_state.get("candidates", []):
#         print(f"- {c.source_doc_id}  (similarity: {c.similarity_score})")

#     print("\n=== RETRIEVAL ATTEMPTS ===")
#     print(final_state.get("retrieval_attempts"))


#     print("\n=== ELIGIBILITY VERDICTS (from Agent 3) ===")
#     for v in final_state.get("verdicts", []):
#         print(f"- {v.scheme_name}: {v.verdict} (confidence: {v.confidence})")
#         if v.missing_info:
#             print(f"    missing: {v.missing_info}")
#         if v.failed_criteria:
#             print(f"    failed: {v.failed_criteria}")

#     print("\n=== FINAL RESULTS (from Agent 4) ===")
#     for r in final_state.get("final_results", []):
#         print(f"- {r.scheme_name}: shown as {r.show_as}")
#         print(f"    {r.plain_language_summary}")
  
#     print("\n=== AUDIT LOG ===")
#     for entry in final_state.get("audit_log", []):
#         print(entry)

# if __name__ == "__main__":
#     run_test()


from unittest import result

from app.core.graph import build_graph

def run_one(graph, raw_input, label):
    print(f"\n{'='*70}\nTEST CASE: {label}\nInput: {raw_input}\n{'='*70}")

    initial_state = {"raw_input": raw_input, "audit_log": []}
    final_state = graph.invoke(initial_state)

    print("\n--- PROFILE ---")
    print(final_state.get("profile"))

    print("--- CANDIDATES RETRIEVED ---")
    for c in final_state["candidates"]:
        print(f"  {c.scheme_name}")

    print("\n--- FINAL RESULTS ---")
    if not final_state.get("final_results"):
        print("(no schemes shown to user — all rejected or filtered out)")
    for r in final_state.get("final_results", []):
        print(f"- {r.scheme_name}: shown as {r.show_as} (confidence: {r.confidence})")
        print(f"    {r.plain_language_summary}")


def run_test():
    graph = build_graph()
    run_one(graph, "I am a girl studying in class 10, my family income is 1.5 lakh per year", "Not currently a student, ambiguous caste")
    run_one(graph, "I am SC category, studying, family income 1.5 lakh per year", "SC student — should produce confirmed_match")


if __name__ == "__main__":
    run_test()