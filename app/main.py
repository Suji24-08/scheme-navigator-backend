# from fastapi import FastAPI
# from app.core.config import settings

# app = FastAPI(title="Scheme Navigator")

# @app.get("/health")
# def health():
#     return {"status": "ok", "mock_mode": settings.MOCK_MODE}

import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from app.core.config import settings
from app.core.graph import build_graph
from app.models.schemas import GraphState
from app.core.audit_db import init_db, save_audit_entry

app = FastAPI(title="Scheme Navigator")
init_db()
# Allow the Next.js frontend (local dev + later Vercel) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your actual Vercel domain once deployed
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

@app.post("/admin/ingest-schemes")
def ingest_schemes_endpoint(x_admin_secret: str = Header(None)):
    if x_admin_secret != os.environ.get("ADMIN_SECRET"):
        raise HTTPException(status_code=403, detail="Forbidden")
    from app.core.vectorstore import ingest_schemes
    count = ingest_schemes()
    return {"status": "ok", "documents_ingested": count}
