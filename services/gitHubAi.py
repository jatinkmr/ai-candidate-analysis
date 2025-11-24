import os
from github import Github, Auth, GithubException

async def fetchGitHubIformation(userName: str) -> dict:
    try:
        accessToken = os.getenv('Github_Access_Token')
        # using an access token
        auth = Auth.Token(accessToken)

        hostname = os.getenv('GITHUB_HOSTNAME')  # Custom GitHub Enterprise hostname

        if hostname:
            base_url = f"https://{hostname}/api/v3"
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

        # Close connection after use
        g.close()

        print("user_info", user_info)

        return user_info

    except GithubException as e:
        # Handle error, e.g., user not found or auth error
        error_message = f"GitHub API Error: {str(e)}"
        raise Exception(error_message)

    except Exception as e:
        # General error handling
        raise Exception(f"Failed to fetch GitHub information: {str(e)}")
