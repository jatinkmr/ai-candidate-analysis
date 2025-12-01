from config.settings import GOOGLE_API_KEY
import google.generativeai as genai
import asyncio


def setup_gemini():
    api_key = GOOGLE_API_KEY
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def _analyze_resume_sync(text: str) -> str:
    """Blocking resume analysis function to run in thread pool."""
    print("Initializing resume analysis...Waiting for response...")

    model = setup_gemini()

    prompt = f"""
        Think like you are an expert resume parser. You will be provided with raw scraped text from a candidate's resume from different formats. The information may be unordered, incomplete, or contain noise.
        Your task is to analyze this text and return a well-structured JSON object that separates the candidate's personal, educational, and professional information.
        Input: {text}. Output: Return only a JSON object with the following structure (fields may be null or empty arrays if information is not available): {{
        "personal_info": {{
            "name": ""
        }},
        "education": [
            {{
                "degree": "", 
                "institution": ""
            }}
        ],
        "professional_experience": [
            {{
                "job_title": "",
                "company": "",
                "start_date": "",
                "end_date": "",
                "location": "",
                "responsibilities": []
            }}
        ],
        "skills": [],
        "certifications": [],
        "projects": []
        }}
    """

    response = model.generate_content(prompt)
    print(f"\nResume Analysis completed!!")

    response_text = response.text.strip()
    if response_text.startswith("```json") and response_text.endswith("```"):
        response_text = response_text[7:-3].strip()  # Remove ```json and ```

    return response_text


async def analyze_resume(text: str) -> str:
    """Async wrapper that runs blocking Gemini call in thread pool."""
    return await asyncio.to_thread(_analyze_resume_sync, text)


def _analyze_github_sync(data: dict) -> str:
    """Blocking GitHub analysis function to run in thread pool."""
    print("Initializing analyze_github GitHub analysis...Waiting for response...")

    model = setup_gemini()

    prompt = f"""
    Think like you are an expert GitHub profile analyzer. You will be provided with GitHub user data including user information and repositories with commits.
    Your task is to analyze this data and return a well-structured JSON object that summarizes the candidate's GitHub activity, inferred skills, activity level, and other insights.
    Input: {data}
    Output: Return only a JSON object with the following structure (fields may be null or empty if information is not available): {{
    "summary": "",
    "skills_inferred": [],
    "activity_level": "",
    "top_repositories": [
        {{
            "name": "",
            "description": "",
            "commits_count": 0,
            "last_commit_date": ""
        }}
    ],
    "commit_patterns": "",
    "languages_used": [],
    "overall_rating": ""
    }}
    """

    response = model.generate_content(prompt)
    print(f"\nGitHub Analysis completed!!")

    response_text = response.text.strip()
    if response_text.startswith("```json") and response_text.endswith("```"):
        response_text = response_text[7:-3].strip()  # Remove ```json and ```

    return response_text


async def analyze_github(data: dict) -> str:
    """Async wrapper that runs blocking Gemini call in thread pool."""
    return await asyncio.to_thread(_analyze_github_sync, data)

    response_text = response.text.strip()
    if response_text.startswith("```json") and response_text.endswith("```"):
        response_text = response_text[7:-3].strip()  # Remove ```json and ```

    return response_text
