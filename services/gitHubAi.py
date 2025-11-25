from config.settings import Github_Access_Token, GITHUB_HOSTNAME
from github import Github, Auth, GithubException

async def fetchGitHubIformation(userName: str) -> dict:
    try:
        accessToken = Github_Access_Token
        auth = Auth.Token(accessToken)

        if GITHUB_HOSTNAME:
            base_url = f"https://{GITHUB_HOSTNAME}/api/v3"
            g = Github(base_url=base_url, auth=auth)
        else:
            # Public Web Github
            g = Github(auth=auth)

        # Fetch the user by provided userName
        user = g.get_user(userName)

        user_info = {
            "login": user.login,
            "name": user.name,
            "bio": user.bio,
            "location": user.location,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "html_url": user.html_url
        }

        # Fetch repositories + commits
        repos_data = []

        repos = user.get_repos()

        for repo in repos:
            repo_info = {
                "name": repo.name,
                "html_url": repo.html_url,
                "commits": []
            }

            try:
                commits = repo.get_commits()
                # Fetch only first N commit messages
                for i, commit in enumerate(commits):
                    repo_info["commits"].append({
                        "message": commit.commit.message,
                    })
            except Exception:
                # e.g. empty repo or no permission
                repo_info["commits"] = []

            repos_data.append(repo_info)

        # Close session
        g.close()

        return {
            "user_info": user_info,
            "repositories": repos_data
        }

    except GithubException as e:
        # Handle error, e.g., user not found or auth error
        error_message = f"GitHub API Error: {str(e)}"
        raise Exception(error_message)

    except Exception as e:
        # General error handling
        raise Exception(f"Failed to fetch GitHub information: {str(e)}")
