import os
from typing import List, Dict, Optional
import json

class MockAIEngine:
    """Mock AI Engine for testing without OpenAI API calls"""
    
    def __init__(self):
        self.policies_ingested = False
        self.mock_policies = [
            "OSFI E-23 requires financial institutions to implement robust model risk management frameworks.",
            "Models must be validated independently before deployment to production environments.",
            "Documentation must include model purpose, methodology, limitations, and performance metrics.",
            "Regular monitoring and back-testing of model performance is mandatory.",
            "Model changes require approval through established governance processes."
        ]
    
    def ingest_osfi_policies(self, policy_text: str) -> None:
        """Mock ingestion of OSFI E-23 policies"""
        print(f"✅ Mock ingestion: Processed {len(policy_text)} characters of policy text")
        self.policies_ingested = True
    
    def generate_model_documentation(self, model_data: Dict) -> str:
        """Generate mock model documentation"""
        model_name = model_data.get('name', 'Unknown Model')
        description = model_data.get('description', 'automated decision making')
        repo_link = model_data.get('repo_link', '')
        
        repo_section = f"""
## 7. Source Code Repository
- Repository: {repo_link}
- Code review: Completed through standard pull request process
- Version control: Git-based with tagged releases
""" if repo_link else ""
        
        documentation = f"""# Model Documentation: {model_name}

## 1. Model Purpose and Business Objective
{description}

This model is designed to support risk management and regulatory compliance activities within the organization.

## 2. Data Sources and Lineage
- Primary data sources: Internal transaction systems
- Data quality: Validated through automated checks
- Update frequency: Daily batch processing

## 3. Model Architecture and Methodology
- Model type: Machine Learning Classification/Regression
- Algorithm: Ensemble methods with cross-validation
- Training approach: Supervised learning with historical data

## 4. Performance Metrics and Validation
- Accuracy: 85-90% on validation dataset
- Precision/Recall: Balanced for business requirements
- Validation method: Independent validation team review

## 5. Limitations and Risk Considerations
- Model performance may degrade with data drift
- Requires regular retraining and monitoring
- Subject to regulatory model risk management requirements

## 6. Deployment and Monitoring
- Deployment environment: Production with A/B testing
- Monitoring: Real-time performance tracking
- Review cycle: Quarterly model performance review{repo_section}
"""
        return documentation
    
    def map_to_osfi_controls(self, model_data: Dict) -> List[Dict]:
        """Generate mock OSFI control mappings"""
        model_name = model_data.get('name', 'Unknown Model')
        
        mappings = []
        for i, policy in enumerate(self.mock_policies):
            mapping = {
                "osfi_control": policy,
                "ai_rationale": f"This control applies to {model_name} because it involves automated decision-making that requires {['governance oversight', 'validation processes', 'documentation standards', 'performance monitoring', 'change management'][i]}.",
                "status": "Proposed",
                "confidence": 0.8 + (i * 0.02)  # Varying confidence scores
            }
            mappings.append(mapping)
        
        return mappings

# Global mock instance for testing
mock_ai_engine = MockAIEngine()