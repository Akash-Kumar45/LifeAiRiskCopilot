# LifeAI Risk Copilot

LifeAI Risk Copilot is an AI governance assistant for financial institutions.  
It helps teams register AI models, auto-generate governance documentation, map model controls to OSFI-style expectations, and view model risk posture in a dashboard.

## Why This Exists

Model governance is usually slow and manual. Teams spend a lot of time preparing documentation, control mappings, and risk summaries for reviewers.

This project accelerates that process by using GenAI to create strong first drafts and structured compliance outputs.

## What The Application Does Today

- Registers AI models (`name`, `version`, `description`, `repo_link`, `status`)
- Stores model metadata in SQLite
- Runs **Analyze with Copilot** to generate:
  - Model documentation
  - OSFI control mappings with rationale
- Calculates consistent model risk (`risk_level`, `risk_score`, `risk_factors`)
- Shows dashboard data from backend APIs (metrics, alerts, model status)

## Current Scope (MVP)

Implemented:
- Model inventory and search/filter
- AI-generated documentation and control mapping
- Live dashboard summary from DB
- Basic role context headers (`x-user-id`, `x-user-role`) and optional API key guard

Planned next:
- Reviewer approval workflow (`Proposed/Approved/Rejected`) with timestamps and notes
- Audit-ready evidence package generation
- Deeper traceability and lifecycle logs

## Tech Stack

- **Frontend**: Next.js 14, React, Tailwind CSS
- **Backend**: FastAPI, SQLModel
- **Database**: SQLite (`backend/lifeai_risk_copilot.db`)
- **AI Provider**: Groq (with fallback handling)

## Project Structure

```text
LifeAiRiskCopilot/
  backend/
    app/
      api/
      services/
      dependencies/
    core/
    data/
    main.py
  frontend/
    src/app/
    src/components/
    src/lib/
  LifeAiRiskCopilot_PRD.md
```

## Setup

## 1) Backend

From repository root:

```powershell
cd backend
..\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Required env vars in `backend/.env`:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
# Optional:
# LIFEAI_API_KEY=your_optional_api_key
```

## 2) Frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:
- `http://localhost:3000`

## Quick Demo Flow

1. Open `/models`
2. Create a model with realistic description and repo link
3. Open model detail page
4. Click **Analyze with Copilot**
5. Review generated documentation + control mappings
6. Open `/dashboard` to view live summary and alerts

## Key APIs

- `POST /api/models`
- `GET /api/models`
- `GET /api/models/{id}`
- `POST /api/models/{id}/analyze`
- `GET /dashboard/metrics`
- `GET /dashboard/summary`
- `GET /dashboard/search`

## Notes

- AI output quality depends heavily on model description quality.
- Generated outputs are best treated as governance drafts requiring human review.
- If Groq model/version changes, set `GROQ_MODEL` in `backend/.env`.

## License

Internal/Project-specific (add your preferred license before public release).

