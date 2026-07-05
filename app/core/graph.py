from langgraph.graph import StateGraph, END
from app.models.schemas import GraphState
from app.agents.profile_extraction import profile_extraction_node
from app.agents.scheme_retrieval import scheme_retrieval_node
from app.agents.eligibility_reasoning import eligibility_reasoning_node
from app.agents.explainer_router import explainer_router_node
from app.agents.guardrail import guardrail_node
# ---- Placeholder node functions (real logic comes in later steps) ----

# def profile_extraction_node(state: GraphState) -> dict:
#     print("[Agent 1] Profile Extraction — placeholder")
#     state.audit_log.append({"agent": "profile_extraction", "action": "ran (stub)"})
#     return {"audit_log": state.audit_log}


# def scheme_retrieval_node(state: GraphState) -> dict:
#     print("[Agent 2] Scheme Retrieval — placeholder")
#     state.audit_log.append({"agent": "scheme_retrieval", "action": "ran (stub)"})
#     return {"audit_log": state.audit_log}


# def eligibility_reasoning_node(state: GraphState) -> dict:
#     print("[Agent 3] Eligibility Reasoning — placeholder")
#     state.audit_log.append({"agent": "eligibility_reasoning", "action": "ran (stub)"})
#     return {"audit_log": state.audit_log}


# def explainer_router_node(state: GraphState) -> dict:
#     print("[Agent 4] Explainer / Confidence Router — placeholder")
#     state.audit_log.append({"agent": "explainer_router", "action": "ran (stub)"})
#     return {"audit_log": state.audit_log}


# ---- Build the graph ----

# def build_graph():
#     graph = StateGraph(GraphState)

#     graph.add_node("profile_extraction", profile_extraction_node)
#     graph.add_node("scheme_retrieval", scheme_retrieval_node)
#     graph.add_node("eligibility_reasoning", eligibility_reasoning_node)
#     graph.add_node("explainer_router", explainer_router_node)

#     graph.set_entry_point("profile_extraction")
#     graph.add_edge("profile_extraction", "scheme_retrieval")
#     graph.add_edge("scheme_retrieval", "eligibility_reasoning")
#     graph.add_edge("eligibility_reasoning", "explainer_router")
#     graph.add_edge("explainer_router", END)

#     return graph.compile()

def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("guardrail", guardrail_node)
    graph.add_node("profile_extraction", profile_extraction_node)
    graph.add_node("scheme_retrieval", scheme_retrieval_node)
    graph.add_node("eligibility_reasoning", eligibility_reasoning_node)
    graph.add_node("explainer_router", explainer_router_node)

    graph.set_entry_point("guardrail")

    graph.add_conditional_edges(
        "guardrail",
        lambda state: "continue" if state.is_on_topic else "stop",
        {
            "continue": "profile_extraction",
            "stop": END,
        },
    )

    graph.add_edge("profile_extraction", "scheme_retrieval")
    graph.add_edge("scheme_retrieval", "eligibility_reasoning")
    graph.add_edge("eligibility_reasoning", "explainer_router")
    graph.add_edge("explainer_router", END)

    return graph.compile()