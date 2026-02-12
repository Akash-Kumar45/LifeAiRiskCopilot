from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import datetime

from app.api.models_router import router as models_router
from app.api.ai_router import router as ai_router
from app.models import AIModel, ControlMapping
from app.services.risk_scoring import assess_db_model_risk
from core.database import create_db_and_tables, engine

app = FastAPI(title="LifeAI Risk Copilot - API")

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models_router, prefix="/api", tags=["models"])
app.include_router(ai_router, prefix="/api", tags=["ai"])


@app.get("/dashboard/metrics")
def get_dashboard_metrics():
    with Session(engine) as session:
        models = session.exec(select(AIModel)).all()
        control_mappings = session.exec(select(ControlMapping)).all()

    mappings_by_model: dict[int, list[ControlMapping]] = {}
    for mapping in control_mappings:
        if mapping.model_id is None:
            continue
        mappings_by_model.setdefault(mapping.model_id, []).append(mapping)

    total_models = len(models)
    active_models = sum(1 for model in models if (model.status or "").lower() == "active")
    high_risk_models = sum(1 for model in models if assess_db_model_risk(model, mappings_by_model.get(model.id or -1, []))["risk_level"] == "High")
    open_gaps = sum(1 for mapping in control_mappings if (mapping.status or "").lower() == "gap")
    controls_verified = sum(
        1
        for mapping in control_mappings
        if (mapping.status or "").lower() in {"approved", "implemented"}
    )

    return {
        "total_models": total_models,
        "active_models": active_models,
        "high_risk_models": high_risk_models,
        "open_gaps": open_gaps,
        "controls_verified": controls_verified,
    }

@app.get("/dashboard/search")
def search_dashboard(q: str = ""):
    """Dashboard search across models and control mappings."""
    term = q.strip()
    if not term:
        return []

    with Session(engine) as session:
        model_results = session.exec(
            select(AIModel).where(
                (AIModel.name.contains(term)) | (AIModel.description.contains(term))
            )
        ).all()
        control_results = session.exec(
            select(ControlMapping).where(
                (ControlMapping.osfi_control_id.contains(term)) | (ControlMapping.rationale.contains(term))
            )
        ).all()

    models_payload = [
        {
            "id": str(model.id),
            "name": model.name,
            "type": "model",
            "category": model.status or "draft",
            "severity": "medium",
        }
        for model in model_results
    ]

    controls_payload = [
        {
            "id": str(mapping.id),
            "name": mapping.osfi_control_id,
            "type": "control",
            "category": mapping.status or "proposed",
            "severity": "high" if (mapping.status or "").lower() == "gap" else "medium",
        }
        for mapping in control_results
    ]

    return models_payload + controls_payload


@app.get("/dashboard/summary")
def dashboard_summary():
    with Session(engine) as session:
        models = session.exec(select(AIModel)).all()
        mappings = session.exec(select(ControlMapping)).all()

    mappings_by_model: dict[int, list[ControlMapping]] = {}
    for mapping in mappings:
        if mapping.model_id is None:
            continue
        mappings_by_model.setdefault(mapping.model_id, []).append(mapping)

    metrics = get_dashboard_metrics()

    recent_alerts = []
    for model in models:
        model_mappings = mappings_by_model.get(model.id or -1, [])
        gap_count = sum(1 for m in model_mappings if (m.status or "").lower() == "gap")
        if gap_count > 0:
            recent_alerts.append(
                {
                    "id": f"gap-{model.id}",
                    "title": "Control Gaps Detected",
                    "model_name": model.name,
                    "severity": "high",
                    "created_at": model.created_at.isoformat(),
                    "details": f"{gap_count} control gap(s) require review.",
                }
            )
        else:
            recent_alerts.append(
                {
                    "id": f"update-{model.id}",
                    "title": "Model Registered/Updated",
                    "model_name": model.name,
                    "severity": "low",
                    "created_at": model.created_at.isoformat(),
                    "details": "Model is in the inventory and ready for ongoing review.",
                }
            )

    recent_alerts = sorted(recent_alerts, key=lambda x: x["created_at"], reverse=True)[:5]

    model_status = []
    for model in models:
        model_mappings = mappings_by_model.get(model.id or -1, [])
        gap_count = sum(1 for m in model_mappings if (m.status or "").lower() == "gap")
        risk = assess_db_model_risk(model, model_mappings)
        model_status.append(
            {
                "id": str(model.id),
                "name": model.name,
                "status": (model.status or "draft").capitalize(),
                "risk_level": risk["risk_level"],
                "risk_score": risk["risk_score"],
                "risk_factors": risk["risk_factors"],
                "controls_total": len(model_mappings),
                "gaps": gap_count,
                "last_updated": model.created_at.isoformat(),
            }
        )

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "metrics": metrics,
        "recent_alerts": recent_alerts,
        "model_status": model_status,
    }

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
