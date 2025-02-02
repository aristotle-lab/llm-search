import re
from google.cloud import storage
import google.auth

# -------------------------------
# Step 1: Authenticate and Initialize the GCS Client
# -------------------------------
credentials, project_id = google.auth.default()
client = storage.Client(credentials=credentials, project=project_id)

# Replace with your actual bucket name.
bucket_name = "magic_forest_plain"
bucket = client.get_bucket(bucket_name)

# -------------------------------
# Step 2: List the Chapter Files
# -------------------------------
# If your 13 files are stored under a common prefix, e.g., "chapters/", specify that prefix.
blobs = bucket.list_blobs()

# Filter for Markdown files (ending in .md) and sort them.
def get_chapter_files(blobs):
    for blob in blobs:
        if blob.name.endswith('.md'):
            yield blob.name

chapter_files = sorted(get_chapter_files(blobs))
print("Found chapter files:")
for f in chapter_files:
    print("  ", f)

# -------------------------------
# Step 3: Define a Function to Split Text into Chunks
# -------------------------------
def split_text(text, max_chunk_length=500):
    """
    Splits text into smaller chunks with each chunk not exceeding max_chunk_length characters.
    This implementation uses sentence boundaries.
    """
    # Split text by sentence endings.
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        # If adding this sentence exceeds our max length, save the current chunk and start a new one.
            current_chunk += f" {sentence}"
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# -------------------------------
# Step 4: Process Each Chapter File and Prepare Data for Indexing
# -------------------------------
data_for_indexing = []  # This list will hold tuples of (vector_id, text_chunk, metadata)

for file_index, file_name in enumerate(chapter_files, start=0):
    # Download the chapter file.
    blob = bucket.blob(file_name)
    chapter_text = blob.download_as_string().decode('utf-8')
    
    # Optionally, extract a chapter title.
    # For example, assume the first non-empty line is the chapter title.
    lines = chapter_text.splitlines()
    chapter_title = None
    for line in lines:
        if line.strip():
            chapter_title = line.strip()
            break
    if not chapter_title:
        chapter_title = f"Chapter {file_index + 1}"
    
    # Split the chapter text into smaller chunks.
    chunks = split_text(chapter_text, max_chunk_length=500)
    
    # For each chunk, prepare a unique ID and metadata.
    for chunk_index, chunk in enumerate(chunks):
        chunk_id = f"chapter{file_index}_chunk{chunk_index}"
        metadata = {
            "chapter_file": file_name,
            "chapter_number": file_index,
            "chapter_title": chapter_title,
            "chunk_index": chunk_index,
            "text": chunk  # include the chunk text as metadata for reference (optional)
        }
        data_for_indexing.append((chunk_id, chunk, metadata))

print(f"Prepared data for indexing. Total chunks: {len(data_for_indexing)}")

# -------------------------------
# (Optional) Example: Print the First Prepared Entry
# -------------------------------
if data_for_indexing:
    example_id, example_text, example_metadata = data_for_indexing[0]
    print("\nExample prepared entry:")
    print("ID:", example_id)
    print("Metadata:", example_metadata)
    print("Text snippet:", example_text[:200])


def get_embedding(text, model="text-embedding-ada-002"):
    response = openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

# Generate embeddings for all chunks
vectors = []  # List to hold tuples (vector_id, embedding, metadata)
for vector_id, chunk, metadata in data_for_indexing:
    try:
        embedding = get_embedding(chunk)
        vectors.append((vector_id, embedding, metadata))
        print(f"Generated embedding for {vector_id}")
    except Exception as e:
        print(f"Error generating embedding for {vector_id}: {e}")