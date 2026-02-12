import os
import requests
from typing import List, Dict, Optional
from groq import Groq
import json
import re
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

class GroqAIEngine:
    """Groq AI Engine for fast model analysis"""
    
    def __init__(self):
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            self.client = Groq(api_key=api_key)
            self.ai_enabled = True
        else:
            self.client = None
            self.ai_enabled = False
            print("Warning: Groq API key not found. AI features will use fallback responses.")
        
        self.osfi_policies = self._load_osfi_policies()
    
    def _load_osfi_policies(self) -> str:
        """Load OSFI E-23 policies from file"""
        try:
            with open("data/osfi_e23.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "OSFI E-23 policies not found"
    
    def _fetch_github_content(self, repo_url: str) -> str:
        """Fetch repository content from GitHub"""
        if not repo_url:
            return ""
        
        try:
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) < 2:
                return ""
            
            owner, repo = parts[0], parts[1].replace(".git", "")
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                return ""
            
            files = response.json()
            content = ""
            
            for file in files[:5]:  # Limit to first 5 files
                if file["name"].endswith((".py", ".md", ".txt")):
                    file_response = requests.get(file["download_url"])
                    if file_response.status_code == 200:
                        content += f"\n--- {file['name']} ---\n"
                        content += file_response.text[:1500]  # Limit content
            
            return content
        except Exception as e:
            print(f"Error fetching GitHub content: {e}")
            return ""
    
    def generate_model_documentation(self, model_data: Dict) -> str:
        """Generate model documentation using Groq"""
        model_name = (model_data.get('name') or 'Unknown Model').strip()
        description = (model_data.get('description') or '').strip()
        repo_url = (model_data.get('repo_link') or '').strip()
        version = (model_data.get('version') or '').strip()
        status = (model_data.get('status') or '').strip()
        
        if not self.ai_enabled:
            return self._generate_fallback_documentation(model_name, description, repo_url)
        
        github_content = self._fetch_github_content(repo_url)
        
        prompt = f"""Generate concise model documentation for a financial AI model following OSFI E-23 requirements.

Model Information:
- Name: {model_name}
- Version: {version or "Not provided"}
- Description: {description}
- Status: {status or "Not provided"}
- Repository: {repo_url}

Code Content:
{github_content[:2000] if github_content else "No code repository provided"}

Generate documentation with these sections:
1. Model Purpose and Business Objective
2. Data Sources and Lineage
3. Model Architecture and Methodology
4. Performance Metrics and Validation
5. Limitations and Risk Considerations
6. Deployment and Monitoring

Rules:
- Do not use placeholders like "[insert ...]", "<...>", "TBD", or "to be provided".
- If information is unavailable, write "Not provided" with a short practical recommendation.
- Keep content concrete to this model and avoid generic boilerplate.
- Output markdown only."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert in financial AI model documentation and regulatory compliance. Be concise and specific."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            raw_content = response.choices[0].message.content or ""
            return self._clean_placeholder_text(raw_content)
        except Exception as e:
            print(f"Error generating documentation: {e}")
            return self._generate_fallback_documentation(model_name, description, repo_url)
    
    def map_to_osfi_controls(self, model_data: Dict) -> List[Dict]:
        """Map model to OSFI controls using Groq analysis"""
        model_name = model_data.get('name', 'Unknown Model')
        description = model_data.get('description', '')
        repo_url = model_data.get('repo_link', '')
        
        if not self.ai_enabled:
            return self._generate_fallback_controls(model_name, description)
        
        github_content = self._fetch_github_content(repo_url)
        
        prompt = f"""Analyze this AI model and map it to relevant OSFI E-23 controls.

Model Information:
- Name: {model_name}
- Description: {description}

Code Analysis:
{github_content[:1500] if github_content else "No code repository provided"}

OSFI E-23 Policies:
{self.osfi_policies[:1500]}

Return JSON array with 5 most relevant controls:
[
    {{
        "osfi_control": "specific control text",
        "ai_rationale": "brief explanation",
        "status": "Proposed"
    }}
]

Focus on the most critical controls for this model type."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert in financial regulatory compliance. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )

            content = response.choices[0].message.content or ""
            controls = self._parse_controls_json(content)
            return controls
        except Exception as e:
            print(f"Error mapping OSFI controls: {e}")
            return self._generate_fallback_controls(model_name, description)

    def _parse_controls_json(self, raw: str) -> List[Dict]:
        """Parse control mappings even when JSON is wrapped in markdown/text."""
        text = raw.strip()
        if not text:
            raise ValueError("Empty response from Groq for control mapping")

        # Strip fenced code blocks if present (```json ... ``` or ``` ... ```).
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

        # First, try direct parse.
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

        # Fallback: extract first JSON array in the text.
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            parsed = json.loads(candidate)
            if isinstance(parsed, list):
                return parsed

        raise ValueError("Could not parse JSON array for control mappings")

    def _clean_placeholder_text(self, text: str) -> str:
        """Replace low-quality placeholder artifacts with deterministic phrasing."""
        cleaned = text
        cleaned = re.sub(r"\[insert[^\]]*\]", "Not provided", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<[^>]{1,80}>", "Not provided", cleaned)
        cleaned = re.sub(r"\bTBD\b", "Not provided", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bto be provided\b", "Not provided", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def _generate_fallback_documentation(self, model_name: str, description: str, repo_url: str) -> str:
        """Generate fallback documentation when Groq is not available"""
        return f"""# Model Documentation: {model_name}

## Model Purpose and Business Objective
{description or "AI model for financial risk management and decision support."}

## Data Sources and Lineage
- Data sources to be documented
- Data quality and validation processes required

## Model Architecture and Methodology
- Model architecture details to be provided
- Algorithm and methodology documentation required

## Performance Metrics and Validation
- Model performance metrics to be established
- Validation methodology and results

## Limitations and Risk Considerations
- Model limitations and assumptions
- Risk factors and mitigation strategies

## Deployment and Monitoring
- Deployment architecture and infrastructure
- Monitoring and alerting systems

{f"Repository: {repo_url}" if repo_url else ""}

*Note: This is a template. Please provide Groq API key for AI-generated content.*"""
    
    def _generate_fallback_controls(self, model_name: str, description: str) -> List[Dict]:
        """Generate fallback OSFI controls when Groq is not available"""
        return [
            {
                "osfi_control": "Model risk management framework establishment",
                "ai_rationale": f"The {model_name} requires a comprehensive risk management framework.",
                "status": "Proposed"
            },
            {
                "osfi_control": "Model validation and testing requirements",
                "ai_rationale": "Independent validation and testing processes must be established.",
                "status": "Gap"
            },
            {
                "osfi_control": "Data quality and management standards",
                "ai_rationale": "Robust data quality controls are essential for model performance.",
                "status": "Proposed"
            }
        ]

# Global instance
groq_ai_engine = GroqAIEngine()
