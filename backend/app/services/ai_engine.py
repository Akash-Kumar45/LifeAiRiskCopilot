import os
from typing import List, Dict, Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIEngine:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=self.openai_api_key)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="../.chroma")
        self.policies_collection = self.chroma_client.get_or_create_collection(
            name="osfi_policies",
            metadata={"description": "OSFI E-23 policy controls"}
        )
    
    def ingest_osfi_policies(self, policy_text: str) -> None:
        """Ingest OSFI E-23 policies into vector database"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        chunks = text_splitter.split_text(policy_text)
        
        for i, chunk in enumerate(chunks):
            embedding = self.embeddings.embed_query(chunk)
            self.policies_collection.add(
                embeddings=[embedding],
                documents=[chunk],
                ids=[f"osfi_chunk_{i}"],
                metadatas=[{"source": "OSFI_E23", "chunk_id": i}]
            )
    
    def generate_model_documentation(self, model_data: Dict) -> str:
        """Generate model documentation using LLM"""
        prompt = f"""
        Generate comprehensive model documentation for the following AI model:
        
        Model Name: {model_data.get('name', 'Unknown')}
        Version: {model_data.get('version', 'Unknown')}
        Description: {model_data.get('description', 'No description provided')}
        
        Please include the following sections:
        1. Model Purpose and Business Objective
        2. Data Sources and Lineage
        3. Model Architecture and Methodology
        4. Performance Metrics and Validation
        5. Limitations and Risk Considerations
        6. Deployment and Monitoring
        
        Format as structured markdown.
        """
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def map_to_osfi_controls(self, model_data: Dict) -> List[Dict]:
        """Map model to OSFI E-23 controls using vector search"""
        model_context = f"""
        Model: {model_data.get('name')}
        Description: {model_data.get('description')}
        Status: {model_data.get('status')}
        """
        
        # Search for relevant controls
        query_embedding = self.embeddings.embed_query(model_context)
        results = self.policies_collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        mappings = []
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            # Generate mapping rationale using LLM
            rationale_prompt = f"""
            Based on this model context:
            {model_context}
            
            And this OSFI control:
            {doc}
            
            Provide a brief rationale for why this control applies to this model, or state "Not Applicable" if it doesn't apply.
            """
            
            rationale_response = self.llm.invoke(rationale_prompt)
            
            mappings.append({
                "osfi_control": doc[:200] + "...",  # Truncate for display
                "ai_rationale": rationale_response.content,
                "status": "Proposed",
                "confidence": 0.8  # Placeholder confidence score
            })
        
        return mappings

# Global instance
ai_engine = AIEngine()