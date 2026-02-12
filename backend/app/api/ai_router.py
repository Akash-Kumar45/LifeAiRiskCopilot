from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.database import get_session
from app.models import AIModel, ControlMapping
from app.services.groq_ai_engine import groq_ai_engine
from app.dependencies.auth import UserContext, get_user_context
from app.services.risk_scoring import assess_model_risk

router = APIRouter()

@router.post("/models/{model_id}/analyze")
def analyze_model(
    model_id: int,
    session: Session = Depends(get_session),
    _user: UserContext = Depends(get_user_context),
) -> Any:
    """Run AI analysis on the model and return updated model with documentation and controls."""
    model = session.get(AIModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    model_data = {
        "name": model.name,
        "version": model.version,
        "description": model.description,
        "status": model.status,
        "repo_link": model.repo_link
    }

    name = (model.name or "").strip()
    version = (model.version or "").strip()
    description = (model.description or "").strip()
    if not name or not version:
        raise HTTPException(
            status_code=422,
            detail="Model name and version are required for analysis.",
        )
    if len(description) < 10:
        raise HTTPException(
            status_code=422,
            detail="Please provide a more detailed model description (at least 10 characters) before analysis.",
        )
    
    try:
        control_mappings = groq_ai_engine.map_to_osfi_controls(model_data)
        documentation = groq_ai_engine.generate_model_documentation(model_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")

    risk = assess_model_risk(
        status=model.status,
        description=model.description,
        repo_link=model.repo_link,
        mapping_statuses=[control.get("status", "") for control in control_mappings],
    )

    # Return model detail format expected by frontend
    return {
        "id": str(model.id),
        "name": model.name,
        "description": model.description,
        "governance_status": model.status,
        "risk_level": risk["risk_level"],
        "risk_score": risk["risk_score"],
        "risk_factors": risk["risk_factors"],
        "created_at": model.created_at.isoformat(),
        "updated_at": model.created_at.isoformat(),
        "documentation": documentation,
        "controls": control_mappings
    }
