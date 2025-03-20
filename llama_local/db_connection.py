import psycopg2
import json  # Import the json module for handling JSON conversion

# Database connection parameters
conn = psycopg2.connect(
    dbname="llm_search",
    user="postgres",
    password="fusion",
    host="localhost",
    port=5432
)
cursor = conn.cursor()

# Create the embeddings table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    embedding VECTOR(384), -- Replace 384 with the dimensionality of your vectors
    metadata JSONB
);
"""
# Ensure the pgvector extension is enabled
enable_pgvector_query = "CREATE EXTENSION IF NOT EXISTS vector;"

try:
    # Enable the pgvector extension
    cursor.execute(enable_pgvector_query)
    # Create the embeddings table
    cursor.execute(create_table_query)
    conn.commit()
    print("Table 'embeddings' is ready.")
except Exception as e:
    print(f"Error creating table: {e}")
    conn.rollback()

# Insert sample vectors into the embeddings table
insert_vector_query = """
INSERT INTO embeddings (embedding, metadata)
VALUES (%s, %s);
"""
sample_vectors = [
    ([0.1] * 384, {"description": "Sample vector 1"}),
    ([0.2] * 384, {"description": "Sample vector 2"}),
    ([0.3] * 384, {"description": "Sample vector 3"}),
]

try:
    for vector, metadata in sample_vectors:
        # Convert the metadata dictionary to a JSON string
        cursor.execute(insert_vector_query, (vector, json.dumps(metadata)))
    conn.commit()
    print("Sample vectors inserted successfully.")
except Exception as e:
    print(f"Error inserting vectors: {e}")
    conn.rollback()

# Test query to check the embeddings table
try:
    cursor.execute("SELECT id, metadata FROM embeddings LIMIT 5;")
    result = cursor.fetchall()
    print("Test query result:", result)
except Exception as e:
    print(f"Error querying table: {e}")

cursor.close()
conn.close()