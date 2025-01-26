import requests
import os


def fetch_repos_issues_by_name(repo_name: str, owner: str, issue_count=10):
  token = os.getenv('GITHUB_API_KEY')
  if token is None:
    raise Exception("GitHub token is required to authenticate the request.")
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
        bodyText
        comments(first: 10) {{
        edges {{
          node {{
          author {{
            login
          }}
          bodyText
          createdAt
          }}
        }}
        }}
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
