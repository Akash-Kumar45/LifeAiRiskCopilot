#!/usr/bin/env python3
"""
Script to ingest OSFI E-23 policies into ChromaDB vector database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_engine import ai_engine

def main():
    """Ingest OSFI E-23 policies into vector database"""
    
    # Read OSFI E-23 policy file
    policy_file = os.path.join(os.path.dirname(__file__), "..", "data", "osfi_e23.txt")
    
    try:
        with open(policy_file, 'r', encoding='utf-8') as f:
            policy_text = f.read()
        
        print("Ingesting OSFI E-23 policies into vector database...")
        ai_engine.ingest_osfi_policies(policy_text)
        print("✅ Successfully ingested OSFI E-23 policies")
        
    except FileNotFoundError:
        print(f"❌ Policy file not found: {policy_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error ingesting policies: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()