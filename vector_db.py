import os
import json
import numpy as np
import faiss
import pdfplumber

from chunking import split_text_into_chunks
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# File paths
INDEX_FILE = "faiss_index.bin"
METADATA_FILE = "metadata.json"
DATA_FOLDER = "pdf_data"

# Extract text from a PDF file
def extract_text_from_pdf(file_path):
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text

# Initialize vector database from existing PDF files
def initialize_from_pdfs():

    if os.path.exists(INDEX_FILE):
        return

    index = None
    metadata = []

    os.makedirs(DATA_FOLDER, exist_ok=True)

    for file_name in os.listdir(DATA_FOLDER):
        if not file_name.endswith(".pdf"):
            continue

        file_path = os.path.join(DATA_FOLDER, file_name)
        text = extract_text_from_pdf(file_path)

        if not text.strip():
            continue

        embedding = model.encode(text).astype("float32")

        if index is None:
            dimension = embedding.shape[0]
            index = faiss.IndexFlatL2(dimension)

        index.add(np.array([embedding]))

        metadata.append({
            "idea": text,
            "source": file_name
        })

    if index is not None:
        faiss.write_index(index, INDEX_FILE)

        with open(METADATA_FILE, "w") as file:
            json.dump(metadata, file, indent=4)
