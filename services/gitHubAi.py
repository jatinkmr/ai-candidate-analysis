from config.settings import Github_Access_Token, GITHUB_HOSTNAME
from github import Github, Auth, GithubException
import asyncio


def _fetchGitHubIformation_sync(userName: str) -> dict:
    """Blocking GitHub API calls to run in thread pool."""
    print("Initializing github analysis...Waiting for response...")
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

        # Get the earliest commit date across all repos to determine active since
        earliest_commit_date = None

        user_info = {
            "username": user.login,
            "name": user.name,
            "bio": user.bio,
            "location": user.location,
            "total_public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "html_url": user.html_url,
        }

        # Fetch repositories + commits
        repos_data = []
        total_commits = 0
        repos = list(user.get_repos())

        for repo in repos:
            repo_info = {"name": repo.name, "html_url": repo.html_url, "commits": []}
            try:
                # Get all commits
                commits = repo.get_commits()

                # Iterate through ALL commits
                for commit in commits:
                    commit_date = (
                        commit.commit.author.date
                        if commit.commit.author and commit.commit.author.date
                        else None
                    )

                    repo_info["commits"].append(
                        {
                            "message": commit.commit.message,
                            "date": commit_date.isoformat() if commit_date else None,
                        }
                    )

                    # Track the earliest commit date
                    if commit_date:
                        if (
                            earliest_commit_date is None
                            or commit_date < earliest_commit_date
                        ):
                            earliest_commit_date = commit_date

                # Count commits for this repo
                total_commits += len(repo_info["commits"])

            except GithubException as e:
                # e.g. empty repo, no permission, or repo is empty
                repo_info["commits"] = []
                repo_info["error"] = str(e)
            except Exception as e:
                repo_info["commits"] = []
                repo_info["error"] = str(e)

            repos_data.append(repo_info)

        # Determine active since date - use the earlier of account creation or first commit
        active_since = user.created_at
        if earliest_commit_date and earliest_commit_date < user.created_at:
            active_since = earliest_commit_date

        user_info["active_since"] = active_since.isoformat() if active_since else None

        # Close session
        g.close()
        print("GitHub session closed.")
        print("Analysis completed!!")

        user_info["total_commits"] = total_commits
        user_info["total_repos"] = len(repos)

        return {"user_info": user_info, "repositories": repos_data}

    except GithubException as e:
        # Handle error, e.g., user not found or auth error
        error_message = f"GitHub API Error: {str(e)}"
        raise Exception(error_message)

    except Exception as e:
        # General error handling
        raise Exception(f"Failed to fetch GitHub information: {str(e)}")


async def fetchGitHubIformation(userName: str) -> dict:
    """Async wrapper that runs blocking PyGithub calls in thread pool."""
    return await asyncio.to_thread(_fetchGitHubIformation_sync, userName)
