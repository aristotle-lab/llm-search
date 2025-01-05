import requests
import functions_framework  # Required for GCP Cloud Functions

@functions_framework.http
def get_sorted_issues(request):
    """
    HTTP Cloud Function that fetches sorted GitHub issues for a given repository.

    Request Parameters (JSON body):
    - owner: Owner of the GitHub repository.
    - repo_name: Name of the GitHub repository.
    - token: GitHub personal access token.
    - issue_count: (Optional) Number of issues to fetch. Default is 10.
    - state: (Optional) State of issues to fetch. Default is OPEN.

    Returns:
        JSON response containing sorted GitHub issues or an error message.
    """
    try:
        # Parse JSON request body
        request_json = request.get_json()
        owner = request_json.get("owner")
        repo_name = request_json.get("repo_name")
        token = request_json.get("token")
        issue_count = request_json.get("issue_count", 10)

        if not owner or not repo_name or not token:
            return {"error": "Missing required parameters: owner, repo_name, or token"}, 400

        query = f"""
        query {{
          repository(owner: "{owner}", name: "{repo_name}") {{
            issues(first: {issue_count}, orderBy: {{ field: CREATED_AT, direction: DESC }}) {{
              edges {{
                node {{
                  title
                  number
                  createdAt
                  url
                }}
              }}
            }}
          }}
        }}
        """

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query},
            headers=headers
        )

        if response.status_code == 200:
            return response.json(), 200
        else:
            return {
                "error": f"GitHub API request failed with status code {response.status_code}",
                "details": response.json()
            }, response.status_code

    except Exception as e:
        return {"error": str(e)}, 500
