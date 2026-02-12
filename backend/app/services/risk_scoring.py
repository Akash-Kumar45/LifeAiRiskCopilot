from typing import Sequence

from app.models import AIModel, ControlMapping


def assess_model_risk(
    status: str | None,
    description: str | None,
    repo_link: str | None,
    mapping_statuses: Sequence[str],
) -> dict:
    score = 30
    reasons: list[str] = []

    status_value = (status or "").strip().lower()
    description_value = (description or "").strip()
    has_repo = bool((repo_link or "").strip())

    if status_value == "draft":
        score += 20
        reasons.append("Model is in draft status and not production-hardened yet.")
    elif status_value == "inactive":
        score += 10
        reasons.append("Model is inactive and may have stale governance artifacts.")
    elif status_value == "active":
        score -= 5
        reasons.append("Model is active with ongoing operational ownership.")

    if len(description_value) < 80:
        score += 10
        reasons.append("Model description is brief; governance context may be incomplete.")
    else:
        score -= 5
        reasons.append("Model description has sufficient context for governance review.")

    if not has_repo:
        score += 10
        reasons.append("No repository link provided for technical traceability.")
    else:
        score -= 5
        reasons.append("Repository link is available for implementation traceability.")

    normalized_statuses = [(s or "").strip().lower() for s in mapping_statuses]
    gap_count = sum(1 for s in normalized_statuses if s == "gap")
    proposed_count = sum(1 for s in normalized_statuses if s == "proposed")
    verified_count = sum(1 for s in normalized_statuses if s in {"approved", "implemented"})

    if gap_count:
        score += gap_count * 20
        reasons.append(f"{gap_count} control gap(s) detected.")
    if proposed_count:
        score += min(20, proposed_count * 5)
        reasons.append(f"{proposed_count} control(s) still in proposed state.")
    if verified_count:
        score -= min(20, verified_count * 5)
        reasons.append(f"{verified_count} control(s) verified as approved/implemented.")

    score = max(0, min(100, score))
    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    if not reasons:
        reasons.append("Insufficient risk signals found; default baseline risk applied.")

    return {"risk_level": level, "risk_score": score, "risk_factors": reasons}


def assess_db_model_risk(model: AIModel, mappings: Sequence[ControlMapping]) -> dict:
    return assess_model_risk(
        status=model.status,
        description=model.description,
        repo_link=model.repo_link,
        mapping_statuses=[m.status or "" for m in mappings],
    )
