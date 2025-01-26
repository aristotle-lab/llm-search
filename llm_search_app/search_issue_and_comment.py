import os
from langchain.embeddings import OpenAIEmbeddings


def hybrid_search(query_text, index, top_k=5):
    """
    Perform a hybrid search across issues, comments, and combined embeddings.

    Args:
        query_text (str): The search query.
        index (Index): Pinecone index instance to query.
        top_k (int): Number of top results to retrieve.

    Returns:
        dict: Results grouped by type (issues, comments, combined).
    """
    # Initialize the OpenAI Embeddings model
    openai_api_key = os.getenv("OPENAI_API_KEY")
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=openai_api_key)

    query_vector = embeddings.embed_query(query_text)

    # Query the index for each type
    results = {}
    for type_filter in ["issue","comment","combined"]:

        results[type_filter] = index.query(
            vector=query_vector,
            top_k=1,
            include_metadata=True,
            filter={"type": type_filter}
        )["matches"]

    return results
  
# # Usage
# outputs = hybrid_search(query_text="nPartialDependenceDisplay", index=index)
# # Display results
# for category, matches in outputs.items():
#     print(f"Results for {category}:")
#     for m in matches:
#         print(f" - Title: {m['metadata'].get('title')}")
#         print(f"   URL: {m['metadata'].get('url')}")
#         print(f"   body: {m['metadata'].get('body', 'N/A')}")
#         print(f"   Score: {m['score']}\n")