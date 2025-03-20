# Create http client
from llama_stack_client import LlamaStackClient

client = LlamaStackClient(base_url="http://localhost:5001")

# Register a vector db
vector_db_id = "pgvector_db"
response = client.vector_dbs.register(
    vector_db_id=vector_db_id,
    embedding_model="all-MiniLM-L6-v2",
    embedding_dimension=384,
    provider_id="pgvector",
)
print(response)

# You can insert a pre-chunked document directly into the vector db
chunks = [
    {
        "metadata": {
            "document_id": "doc1",
        },
        "content": "Your document text here",
        "mime_type": "text/plain",
    },
]
client.vector_io.insert(vector_db_id=vector_db_id, chunks=chunks)

# You can then query for these chunks
chunks_response = client.vector_io.query(
    vector_db_id=vector_db_id, query="What do you know about..."
)
print(chunks_response)