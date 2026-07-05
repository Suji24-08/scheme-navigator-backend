from pydantic import BaseModel, Field
from typing import Optional, Literal


class UserProfile(BaseModel):
    """Structured facts extracted from the user's free-text description."""
    income_monthly: Optional[float] = None
    income_annual: Optional[float] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    family_size: Optional[int] = None
    caste_category: Optional[str] = None  # SC/ST/OBC/General — relevant to many schemes
    disability_status: Optional[bool] = None
    is_student: Optional[bool] = None
    raw_text: str  # original user input, kept for traceability

    # Agent 1's own uncertainty flags — critical for "don't guess silently"
    ambiguous_fields: list[str] = Field(default_factory=list)
    extraction_notes: Optional[str] = None


class SchemeCandidate(BaseModel):
    """A scheme document chunk retrieved from the vector DB."""
    scheme_name: str
    source_chunk: str
    source_doc_id: str
    similarity_score: float


class EligibilityVerdict(BaseModel):
    """Output of the Eligibility Reasoning Agent for ONE scheme."""
    scheme_name: str
    verdict: Literal["eligible", "not_eligible", "insufficient_evidence"]
    matched_criteria: list[str] = Field(default_factory=list)
    failed_criteria: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    citation: str  # exact rule/clause text or doc reference this verdict rests on
    confidence: float  # 0.0–1.0, this feeds the router agent


class FinalExplanation(BaseModel):
    """Output of the Explainer/Confidence Router Agent."""
    scheme_name: str
    show_as: Literal["confirmed_match", "verify_with_local_office", "not_shown"]
    plain_language_summary: str
    citation: str
    confidence: float


class GraphState(BaseModel):
    """The full state object passed through the LangGraph pipeline."""
    raw_input: str
    profile: Optional[UserProfile] = None
    candidates: list[SchemeCandidate] = Field(default_factory=list)
    retrieval_attempts: int = 0
    verdicts: list[EligibilityVerdict] = Field(default_factory=list)
    final_results: list[FinalExplanation] = Field(default_factory=list)
    audit_log: list[dict] = Field(default_factory=list)  # requirement #12 starts here
    is_on_topic: bool = True
    refusal_message: Optional[str] = None