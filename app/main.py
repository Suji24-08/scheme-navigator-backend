import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from app.core.config import settings
from app.core.graph import build_graph
from app.models.schemas import GraphState
from app.core.audit_db import init_db, save_audit_entry

from app.core.vectorstore import get_scheme_document
from app.core.llm_client import call_llm_text


class FollowupRequest(BaseModel):
    scheme_name: str
    question: str


class FollowupResponse(BaseModel):
    answer: str

app = FastAPI(title="Scheme Navigator")
init_db()
# Allow the Next.js frontend (local dev + later Vercel) to call this API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://scheme-navigator-frontend.vercel.app"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://scheme-navigator-frontend.vercel.app",
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
_graph = build_graph()  # compiled once at startup, reused across requests


class EligibilityRequest(BaseModel):
    description: str


class EligibilityResponse(BaseModel):
    profile: dict
    final_results: list[dict]
    audit_log: list[dict]
    refusal_message: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok", "mock_mode": settings.MOCK_MODE}


@app.post("/check-eligibility", response_model=EligibilityResponse)
def check_eligibility(req: EligibilityRequest):
    initial_state = GraphState(raw_input=req.description)
    result = _graph.invoke(initial_state)

    if not result.get("is_on_topic", True):
        return {
            "profile": {},
            "final_results": [],
            "audit_log": result.get("audit_log", []),
            "refusal_message": result.get("refusal_message"),
        }
    
    save_audit_entry(
        raw_input=req.description,
        final_results=[r.model_dump() for r in result.get("final_results", [])],
        audit_log=result.get("audit_log", []),
    )
    
    return {
        "profile": result["profile"].model_dump() if result.get("profile") else {},
        "final_results": [r.model_dump() for r in result.get("final_results", [])],
        "audit_log": result.get("audit_log", []),
    }


@app.post("/ask-followup", response_model=FollowupResponse)
def ask_followup(req: FollowupRequest):
    doc_text = get_scheme_document(req.scheme_name)

    if doc_text is None:
        raise HTTPException(status_code=404, detail="Scheme not found")

    prompt = f"""You are answering a citizen's follow-up question about ONE specific government welfare scheme.
Use ONLY the information in the scheme text below. Do not use outside knowledge.
If the answer isn't in the text, say so clearly instead of guessing.

SCHEME TEXT:
{doc_text}

QUESTION: {req.question}

Answer in 2-4 plain-language sentences."""

    mock_answer = (
        f"[MOCK] Based on the {req.scheme_name} scheme document, "
        f"here is a sample answer to: '{req.question}'. "
        "This is placeholder text since MOCK_MODE is on."
    )

    answer = call_llm_text(prompt, mock_answer)
    return {"answer": answer}

@app.post("/admin/ingest-schemes")
def ingest_schemes_endpoint(x_admin_secret: str = Header(None)):
    if x_admin_secret != os.environ.get("ADMIN_SECRET"):
        raise HTTPException(status_code=403, detail="Forbidden")
    from app.core.vectorstore import ingest_schemes
    count = ingest_schemes()
    return {"status": "ok", "documents_ingested": count}
