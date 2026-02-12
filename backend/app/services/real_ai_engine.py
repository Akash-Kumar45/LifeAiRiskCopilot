import os
import requests
from typing import List, Dict, Optional
import openai
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

class RealAIEngine:
    """Real AI Engine using OpenAI for model analysis"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.ai_enabled = True
        else:
            self.client = None
            self.ai_enabled = False
            print("Warning: OpenAI API key not found. AI features will use fallback responses.")
        
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
            # Extract owner/repo from URL
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) < 2:
                return ""
            
            owner, repo = parts[0], parts[1].replace(".git", "")
            
            # Get repository files via GitHub API
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                return ""
            
            files = response.json()
            content = ""
            
            # Get README and Python files
            for file in files[:10]:  # Limit to first 10 files
                if file["name"].endswith((".py", ".md", ".txt", ".ipynb")):
                    file_response = requests.get(file["download_url"])
                    if file_response.status_code == 200:
                        content += f"\n\n--- {file['name']} ---\n"
                        content += file_response.text[:2000]  # Limit content
            
            return content
        except Exception as e:
            print(f"Error fetching GitHub content: {e}")
            return ""
    
    def generate_model_documentation(self, model_data: Dict) -> str:
        """Generate real model documentation using OpenAI"""
        model_name = model_data.get('name', 'Unknown Model')
        description = model_data.get('description', '')
        repo_url = model_data.get('repo_link', '')
        
        if not self.ai_enabled:
            return self._generate_fallback_documentation(model_name, description, repo_url)
        
        # Fetch GitHub content if available
        github_content = self._fetch_github_content(repo_url)
        
        prompt = f"""
        Generate comprehensive model documentation for a financial AI model following OSFI E-23 requirements.
        
        Model Information:
        - Name: {model_name}
        - Description: {description}
        - Repository: {repo_url}
        
        GitHub Code Content:
        {github_content[:3000] if github_content else "No code repository provided"}
        
        Generate documentation with these sections:
        1. Model Purpose and Business Objective
        2. Data Sources and Lineage
        3. Model Architecture and Methodology
        4. Performance Metrics and Validation
        5. Limitations and Risk Considerations
        6. Deployment and Monitoring
        7. Source Code Repository (if provided)
        
        Make it specific to the model based on the code and description provided.
        Format as markdown with proper headers.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in financial AI model documentation and regulatory compliance."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating documentation: {e}")
            return self._generate_fallback_documentation(model_name, description, repo_url)
    
    def map_to_osfi_controls(self, model_data: Dict) -> List[Dict]:
        """Map model to OSFI controls using AI analysis"""
        model_name = model_data.get('name', 'Unknown Model')
        description = model_data.get('description', '')
        repo_url = model_data.get('repo_link', '')
        
        if not self.ai_enabled:
            return self._generate_fallback_controls(model_name, description)
        
        # Fetch GitHub content if available
        github_content = self._fetch_github_content(repo_url)
        
        prompt = f"""
        Analyze this AI model and map it to relevant OSFI E-23 controls.
        
        Model Information:
        - Name: {model_name}
        - Description: {description}
        - Repository: {repo_url}
        
        Code Analysis:
        {github_content[:2000] if github_content else "No code repository provided"}
        
        OSFI E-23 Policies:
        {self.osfi_policies[:2000]}
        
        For each relevant OSFI control, provide:
        1. The specific OSFI control requirement
        2. AI rationale explaining why it applies to this model
        3. Status (Proposed/Gap/Implemented)
        
        Return as JSON array with format:
        [
            {{
                "osfi_control": "specific control text",
                "ai_rationale": "detailed explanation",
                "status": "Proposed"
            }}
        ]
        
        Focus on the most relevant 5-7 controls based on the model's complexity and risk.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in financial regulatory compliance and AI model risk management. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            import json
            controls = json.loads(response.choices[0].message.content)
            return controls
        except Exception as e:
            print(f"Error mapping OSFI controls: {e}")
            return self._generate_fallback_controls(model_name, description)
    
    def _generate_fallback_documentation(self, model_name: str, description: str, repo_url: str) -> str:
        """Generate fallback documentation when OpenAI is not available"""
        return f"""# Model Documentation: {model_name}

## Model Purpose and Business Objective
{description or "AI model for financial risk management and decision support."}

## Data Sources and Lineage
- Data sources to be documented
- Data quality and validation processes required
- Data lineage tracking needed

## Model Architecture and Methodology
- Model architecture details to be provided
- Algorithm and methodology documentation required
- Feature engineering and selection process

## Performance Metrics and Validation
- Model performance metrics to be established
- Validation methodology and results
- Backtesting and stress testing requirements

## Limitations and Risk Considerations
- Model limitations and assumptions
- Risk factors and mitigation strategies
- Regulatory compliance considerations

## Deployment and Monitoring
- Deployment architecture and infrastructure
- Monitoring and alerting systems
- Model performance tracking

## Source Code Repository
{f"Repository: {repo_url}" if repo_url else "No repository provided"}

*Note: This is a template documentation. Please provide OpenAI API key for AI-generated content.*
"""
    
    def _generate_fallback_controls(self, model_name: str, description: str) -> List[Dict]:
        """Generate fallback OSFI controls when OpenAI is not available"""
        return [
            {
                "osfi_control": "Model risk management framework establishment",
                "ai_rationale": f"The {model_name} requires a comprehensive risk management framework to ensure proper governance and oversight.",
                "status": "Proposed"
            },
            {
                "osfi_control": "Model validation and testing requirements",
                "ai_rationale": "Independent validation and testing processes must be established to verify model accuracy and reliability.",
                "status": "Gap"
            },
            {
                "osfi_control": "Data quality and management standards",
                "ai_rationale": "Robust data quality controls are essential for model performance and regulatory compliance.",
                "status": "Proposed"
            },
            {
                "osfi_control": "Model documentation and change management",
                "ai_rationale": "Comprehensive documentation and change management processes are required for audit and compliance purposes.",
                "status": "Gap"
            },
            {
                "osfi_control": "Ongoing monitoring and performance tracking",
                "ai_rationale": "Continuous monitoring systems must be implemented to track model performance and detect degradation.",
                "status": "Proposed"
            }
        ]

# Global instance
real_ai_engine = RealAIEngine()
