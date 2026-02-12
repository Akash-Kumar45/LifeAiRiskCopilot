"""Simple script to ingest a policy text file into local Chroma vector store.

Usage:
  python scripts/ingest_policy.py path/to/osfi_e23.txt

This script will split the text into chunks and store them with metadata containing a guessed control id if present.
"""
import sys
from pathlib import Path
from typing import List
from dotenv import load_dotenv

load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def ingest(file_path: str, collection_name: str = "osfi_e23", persist_dir: str = "./.chroma") -> None:
    text = Path(file_path).read_text(encoding="utf-8")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    docs = splitter.split_text(text)

    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    chroma = Chroma(collection_name=collection_name, embedding_function=embedding, persist_directory=persist_dir)

    # Attempt to assign a control_id from headings like "E-23.1" or "Control 1"
    metadatas = []
    for d in docs:
        # crude heuristic: first 30 chars may contain control id
        first = d.strip().splitlines()[0] if d.strip() else ""
        control_id = None
        # extract token like E-23-1 or E-23.1
        import re

        m = re.search(r"(E[- ]?23[- .]?\d+)", first, flags=re.IGNORECASE)
        if m:
            control_id = m.group(1)
        metadatas.append({"control_id": control_id or "unknown"})

    chroma.add_texts(docs, metadatas=metadatas)
    print(f"Ingested {len(docs)} chunks into Chroma collection '{collection_name}'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest_policy.py path/to/osfi_e23.txt")
        sys.exit(1)
    ingest(sys.argv[1])
