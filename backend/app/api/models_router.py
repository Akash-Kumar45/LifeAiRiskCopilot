from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlmodel import select, Session, or_

from core.database import get_session
from app.models import AIModel, ControlMapping, Evidence
from app.dependencies.auth import UserContext, get_user_context
from app.services.risk_scoring import assess_db_model_risk

router = APIRouter()


class AIModelCreate(BaseModel):
    name: str
    version: str
    status: Optional[str] = "draft"
    description: Optional[str] = None
    repo_link: Optional[str] = None

    @field_validator("name", "version")
    @classmethod
    def non_empty_required_fields(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Field cannot be empty")
        return value.strip()


class AIModelRead(AIModelCreate):
    id: int
    created_at: datetime


class EvidenceOut(BaseModel):
    id: int
    file_hash: str
    timestamp: datetime
    content_summary: Optional[str]


class ControlMappingOut(BaseModel):
    id: int
    osfi_control_id: str
    rationale: Optional[str]
    status: str
    evidences: List[EvidenceOut] = []


@router.get("/auth/me", response_model=UserContext)
def get_current_user(user: UserContext = Depends(get_user_context)) -> UserContext:
    """Auth placeholder endpoint for validating request context headers."""
    return user


@router.post("/models", response_model=AIModelRead)
def create_model(
    model_in: AIModelCreate,
    session: Session = Depends(get_session),
    _user: UserContext = Depends(get_user_context),
) -> AIModelRead:
    """Register a new AI model (basic metadata)."""
    model = AIModel(**model_in.dict())
    session.add(model)
    session.commit()
    session.refresh(model)
    return AIModelRead(**model.dict())


@router.get("/models", response_model=List[AIModelRead])
def list_models(
    risk: Optional[str] = None,
    status: Optional[str] = None,
    dateFrom: Optional[str] = None,
    dateTo: Optional[str] = None,
    session: Session = Depends(get_session),
    _user: UserContext = Depends(get_user_context),
) -> List[AIModelRead]:
    """List models with optional filters."""
    query = select(AIModel)
    status_value = status.lower() if status else None
    risk_value = risk.lower() if risk else None

    date_from_dt = None
    date_to_dt = None
    if dateFrom:
        try:
            date_from_dt = datetime.fromisoformat(dateFrom)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid dateFrom format. Use ISO format (YYYY-MM-DD).")
    if dateTo:
        try:
            date_to_dt = datetime.fromisoformat(dateTo)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid dateTo format. Use ISO format (YYYY-MM-DD).")

    if status_value:
        query = query.where(AIModel.status == status_value)
    if date_from_dt:
        query = query.where(AIModel.created_at >= date_from_dt)
    if date_to_dt:
        query = query.where(AIModel.created_at <= date_to_dt)
    
    models = session.exec(query).all()
    if risk_value:
        model_ids = [m.id for m in models if m.id is not None]
        all_mappings = session.exec(select(ControlMapping).where(ControlMapping.model_id.in_(model_ids))).all() if model_ids else []
        mappings_by_model: dict[int, list[ControlMapping]] = {}
        for mapping in all_mappings:
            if mapping.model_id is None:
                continue
            mappings_by_model.setdefault(mapping.model_id, []).append(mapping)
        models = [
            model
            for model in models
            if assess_db_model_risk(model, mappings_by_model.get(model.id or -1, []))["risk_level"].lower() == risk_value
        ]
    return [AIModelRead(**m.dict()) for m in models]

@router.get("/models/search", response_model=List[AIModelRead])
def search_models(
    q: str = Query(...),
    session: Session = Depends(get_session),
    _user: UserContext = Depends(get_user_context),
) -> List[AIModelRead]:
    """Search models by name or description."""
    query = select(AIModel).where(
        or_(
            AIModel.name.contains(q),
            AIModel.description.contains(q)
        )
    )
    models = session.exec(query).all()
    return [AIModelRead(**m.dict()) for m in models]

@router.get("/models/{model_id}", response_model=dict)
def get_model(
    model_id: int,
    session: Session = Depends(get_session),
    _user: UserContext = Depends(get_user_context),
) -> dict:
    """Get a specific model by ID with ModelDetail format."""
    model = session.get(AIModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    model_mappings = session.exec(select(ControlMapping).where(ControlMapping.model_id == model_id)).all()
    risk = assess_db_model_risk(model, model_mappings)

    return {
        "id": str(model.id),
        "name": model.name,
        "description": model.description or "",
        "governance_status": model.status,
        "risk_level": risk["risk_level"],
        "risk_score": risk["risk_score"],
        "risk_factors": risk["risk_factors"],
        "created_at": model.created_at.isoformat(),
        "updated_at": model.created_at.isoformat(),
        "documentation": "",  # Empty until analyzed
        "controls": []  # Empty until analyzed
    }
