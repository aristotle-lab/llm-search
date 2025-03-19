import psycopg2

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

# Test query to check the embeddings table
try:
    cursor.execute("SELECT * FROM embeddings LIMIT 1;")
    result = cursor.fetchall()
    print("Test query result:", result)
except Exception as e:
    print(f"Error querying table: {e}")

cursor.close()
conn.close()