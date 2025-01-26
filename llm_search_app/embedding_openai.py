from langchain.embeddings import OpenAIEmbeddings
from pinecone import Index
import logging
import os

def process_issues_and_store_hybrid(issues, index: Index, min_comment_length=10):
    """
    Process GitHub issues and comments, and store their embeddings in Pinecone.

    Args:
        issues (dict): A dictionary containing GitHub issues and comments data.
        index (Index): Pinecone index instance to store embeddings.

    Returns:
        None
    """
    
    # Initialize the OpenAI Embeddings model
    openai_api_key = os.getenv("OPENAI_API_KEY")
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=openai_api_key)

    for issue in issues["data"]["repository"]["issues"]["edges"]:
        issue_node = issue["node"]
        issue_title = issue_node["title"]
        issue_body = issue_node["bodyText"]
        issue_url = issue_node["url"]
        issue_id = issue_node["number"]

        # Embed issue (title + body)
        issue_text = f"Title: {issue_title}\n\nBody: {issue_body}"
        issue_vector = embeddings.embed_query(issue_text)

        # Store issue embedding
        issue_metadata = {
            "type": "issue",
            "title": issue_title,
            "url": issue_url,
            "body": issue_body,
            "createdAt": issue_node["createdAt"],
            "number": issue_id
        }
        index.upsert([(str(issue_id), issue_vector, issue_metadata)])

        # Process and embed comments
        comments = issue_node["comments"]["edges"]
        comment_vectors = []
        comment_texts = []

        for comment in comments:
            comment_node = comment["node"]
            comment_text = comment_node["bodyText"]
            comment_author = comment_node["author"]["login"]
            comment_created_at = comment_node["createdAt"]

            # Skip empty or invalid comments
            if not comment_text or len(comment_text) < 10:
                continue

            # Embed comment
            comment_vector = embeddings.embed_query(comment_text)

            # Prepare comment metadata
            comment_metadata = {
                "type": "comment",
                "comment_text": comment_text,
                "author": comment_author,
                "createdAt": comment_created_at,
                "issue_id": issue_id,
                "issue_title": issue_title
            }
            comment_vectors.append((f"comment-{comment_created_at}", comment_vector, comment_metadata))
            comment_texts.append(f"- {comment_author}: {comment_text}")

        # Store comment embeddings
        if comment_vectors:
            index.upsert(comment_vectors)

        # Embed combined text (issue + comments)
        combined_text = f"Title: {issue_title}\n\nBody: {issue_body}\n\nComments:\n" + "\n".join(comment_texts)
        combined_vector = embeddings.embed_query(combined_text)

        # Store combined embedding
        combined_metadata = {
            "type": "combined",
            "title": issue_title,
            "url": issue_url,
            "body": issue_body,
            "createdAt": issue_node["createdAt"],
            "number": issue_id
        }
        index.upsert([(f"combined-{issue_id}", combined_vector, combined_metadata)])

    logging.info("Issues and comments stored successfully!")