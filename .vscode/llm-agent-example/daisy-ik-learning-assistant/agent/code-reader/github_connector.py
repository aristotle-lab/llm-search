import requests

def fetch_github_repos(username, token=None):
    """
    Fetch the list of GitHub repositories for a given user.

    Args:
        username (str): GitHub username.
        token (str, optional): Personal access token for authentication (if needed).

    Returns:
        list: A list of repositories or an error message.
    """
    url = f"https://api.github.com/users/{username}/repos"
    headers = {}

    if token:
        headers['Authorization'] = f"token {token}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()

        # Extract and print repository names
        repo_list = [repo['name'] for repo in repos]
        return repo_list

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def fetch_repo_file_content(username, repo_name, file_path, token=None):
    """
    Fetch the content of a specific file in a GitHub repository.

    Args:
        username (str): GitHub username.
        repo_name (str): Name of the repository.
        file_path (str): Path to the file in the repository.
        token (str, optional): Personal access token for authentication (if needed).

    Returns:
        str: Content of the file or an error message.
    """
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{file_path}"
    headers = {}

    if token:
        headers['Authorization'] = f"token {token}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        file_content = response.json()

        if 'content' in file_content:
            import base64
            decoded_content = base64.b64decode(file_content['content']).decode('utf-8')
            return decoded_content
        else:
            return "File content not found."

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Replace 'username' with the GitHub username you want to fetch repositories for
    # Replace 'token' with your GitHub Personal Access Token (optional for private repos or higher rate limits)
    username = None  # Replace with the GitHub username
    token = None  # Replace with your GitHub token if needed

    repos = fetch_github_repos(username, token)

    if isinstance(repos, list):
        print(f"Repositories for {username}:")
        for repo in repos:
            print(f"- {repo}")

        # Fetch a file from a specific repository
        repo_name = 'data-structure-practices-python'  # Example: fetch from the first repository
        file_path = "bst/average_of_levels.py"  # Example: fetch README.md file
        file_content = fetch_repo_file_content(username, repo_name, file_path, token)

        print(f"\nContent of {file_path} in {repo_name}:")
        print(file_content)
    else:
        print(repos)
