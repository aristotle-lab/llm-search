import requests


def fetch_repos_issues_by_name(repo_name: str, owner: str, token=None):
    query = f"""
    query {{
      repository(owner: "{owner}", name: "{repo_name}") {{
        issues(orderBy: {{ field: CREATED_AT, direction: DESC }}) {{
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
        return response.json()
    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.json()}")


if __name__ == "__main__":
    repo_name = "scikit-learn"  
    owner = "scikit-learn" 
    token = None  # Replace with your GitHub token if needed

    issues = fetch_repos_issues_by_name(repo_name, owner, token)
    print(issues)
