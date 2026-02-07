import json
import os
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from langchain_huggingface import HuggingFaceEmbeddings

# --- CLOUD CREDENTIALS ---
QDRANT_URL = "https://3afbb0bc-aaf3-49f2-a40c-d2d2c45580bc.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.COF5HUNtq5GzENkLrZdIZDRN9FFoT_q4yy00kdeVaS8"

# CONFIG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
JSON_PATH = os.path.join(PROJECT_ROOT, "data", "atharva_dataset.json")
COLLECTION_NAME = "atharva_knowledge"

def ingest():
    print("--- 1. CONNECTING TO CLOUD BRAIN ---")
    
    # Initialize Embedding Model
    print("Loading AI Model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Initialize Cloud Database
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)
        print(f"Connected to Qdrant Cloud: {QDRANT_URL}")
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    # Reset collection
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    print("--- 2. UPLOADING DATA ---")
    if not os.path.exists(JSON_PATH):
        print(f"ERROR: Could not find {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        hymns = json.load(f)

    print(f"Found {len(hymns)} hymns. Converting and uploading...")

    points = []
    for idx, hymn in enumerate(hymns):
        text_to_embed = f"{hymn['title']}. {hymn['content']}"
        vector = embeddings.embed_query(text_to_embed)
        
        points.append(PointStruct(
            id=idx,
            vector=vector,
            payload={
                "title": hymn['title'],
                "book": hymn['book'],
                "hymn_num": hymn['hymn'],
                "content": hymn['content'],
                "page": hymn['page']
            }
        ))

        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1} hymns...")

    # Upload in batch
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"\n--- SUCCESS: Brain uploaded to Cloud with {len(points)} memories. ---")

if __name__ == "__main__":
    ingest()