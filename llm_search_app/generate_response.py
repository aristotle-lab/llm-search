import os
from openai import OpenAI

def generate_response_from_retrieval(query, retrieval_results):
    """
    Generate a user-friendly response based on retrieval results.

    Args:
        query (str): User's query.
        retrieval_results (dict): Grouped retrieval results by categories.

    Returns:
        str: Generated response.
    """
    # Start building the context
    context = f"User Query: {query}\n\n"

    # Process each category in the retrieval results
    for category, results in retrieval_results.items():
        if results:  # Only include non-empty categories
            context += f"### {category.capitalize()}s:\n"
            for idx, match in enumerate(results, start=1):
                metadata = match.get("metadata", {})
                title = metadata.get("title", "N/A")
                body = metadata.get("body", "N/A")
                comment_text = metadata.get("comment_text", "No comments available")
                url = metadata.get("url", "No URL provided")
                created_at = metadata.get("createdAt", "Unknown date")

                # Add details for each result
                context += f"{idx}. Title: {title}\n"
                context += f"   Created At: {created_at}\n"
                if category == "comment":
                    context += f"   Comment: {comment_text}\n"
                else:
                    context += f"   Description: {body}\n"
                context += f"   URL: {url}\n\n"

    # Combine context into a prompt
    prompt = f"""
    Context:
    {context}

    Based on the above information, provide a helpful response to the user's query.
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

    return completion.choices[0].message.content


# Example usage
# query = "for this issue about OpenML, have it resolved from the comment? could you also provide me the issue link?"
# retrieval_results=hybrid_search(query, index)
# grouped_results = generate_response_from_retrieval(query,retrieval_results)
# print(grouped_results)

