import os
from llama_stack_client import LlamaStackClient

# Set up LlamaStackClient
client = LlamaStackClient(base_url="http://localhost:5001")

# Register vector DB
vector_db_id = "pgvector_db"
response = client.vector_dbs.register(
    vector_db_id=vector_db_id,
    embedding_model="all-MiniLM-L6-v2",
    embedding_dimension=384,
    provider_id="pgvector",
)

# Simple chunking function
def simple_chunk(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Path to your .md files
md_dir = "../sample-docs/magical-forest"
md_files = sorted([f for f in os.listdir(md_dir) if f.endswith(".md")])[:12]  # First 12 md files

all_chunks = []

for i, file_name in enumerate(md_files):
    with open(os.path.join(md_dir, file_name), "r", encoding="utf-8") as f:
        text = f.read()

    chunks = simple_chunk(text)

    for j, chunk in enumerate(chunks):
        all_chunks.append({
            "metadata": {
                "document_id": f"doc{i+1}_chunk{j+1}",
                "source_file": file_name,
            },
            "content": chunk,
            "mime_type": "text/markdown",
        })
        
print(f"Prepared {len(all_chunks)} chunks for indexing.")

# Insert into vector DB
insert_response = client.vector_io.insert(vector_db_id=vector_db_id, chunks=all_chunks)
print("Insert response:", insert_response)

query_result = client.vector_io.query(
    vector_db_id=vector_db_id,
    query="What do you know about the Lily?")
print("Query response:", query_result.chunks[0].content)
print("Query response:", query_result.scores)

user_profiles = [
    {
        "title": "Fantasy Explorer",
        "content": "I love reading about enchanted forests, mythical creatures, and magical lands. Stories like the ones in fantasy novels captivate me.",
    },
    {
        "title": "Nature Enthusiast",
        "content": "Forests, wildlife, and the mystery of the natural world fascinate me. I enjoy exploring hidden trails and learning about trees and plants.",
    },
    {
        "title": "Tech & Sci-Fi Geek",
        "content": "My favorite stories are about future technology, robots, space travel, and artificial intelligence. Not so much into magic.",
    },
]

# Format into chunks
chunks = []
for i, profile in enumerate(user_profiles):
    chunks.append({
        "metadata": {
            "document_id": f"user{i+1}",
            "user_title": profile["title"],
        },
        "content": profile["content"],
        "mime_type": "text/plain",
    })

# Insert into the vector DB
insert_response = client.vector_io.insert(
    vector_db_id=vector_db_id, chunks=chunks
)
print("✅ Inserted user profiles:", insert_response)

# Example query
query_result = client.vector_io.query(
    vector_db_id=vector_db_id,
    query="Fantasy Explorer")
print("Query response:", query_result)
print("Query response:", query_result.scores)