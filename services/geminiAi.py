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
        "projects": [],
        "github_username": "",
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


async def final_analysis(resume_analysis: dict, github_info: dict) -> str:
    """Async wrapper that runs blocking Gemini call in thread pool."""
    return await asyncio.to_thread(
        _final_analysis_sync, resume_analysis, github_info
    )


def _final_analysis_sync(resume_analysis: dict, github_info: dict) -> str:
    """Blocking final analysis function to run in thread pool."""
    print("Initializing final analysis...Waiting for response...")

    model = setup_gemini()

    prompt = f"""
    You are an expert candidate profiling and verification system.

    You will be provided with:
    1. Resume analysis (structured claims)
    2. Raw GitHub data (user profile, repositories, commits)

    You must perform TWO tasks in order:

    TASK 1: GitHub Analysis
    Analyze GitHub data and produce a GitHub analysis using the EXACT structure below.
    Do not reference resume data in this section.

    GitHub Analysis Output Schema:
    {{
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

    TASK 2: Final Credibility Analysis
    Using:
    - Resume analysis
    - GitHub analysis from TASK 1

    Cross-verify claims and produce a credibility assessment.

    Final Analysis Output Schema:
    {{
        "timestamp": "",
        "overall_credibility_score": 0,
        "detailed_scores": {{
            "technology_match_score": 0,
            "project_verification_score": 0,
            "activity_authenticity_score": 0,
            "experience_consistency_score": 0
        }},
        "resume_summary": {{
            "claimed_skills": [],
            "projects_mentioned": 0,
            "experience_years": 0
        }},
        "github_summary": {{
            "total_repositories": 0,
            "total_commits": 0,
            "languages_used": [],
            "active_since": ""
        }},
        "verification_results": {{
            "strengths": [],
            "concerns": []
        }},
        "detailed_analysis": "",
        "recommendations": []
    }}

    RULES:
    - Use only provided data
    - Prefer GitHub evidence over resume claims
    - Do NOT hallucinate data
    - If information is missing, return null or empty values
    - Maintain strict JSON validity

    INPUT:
    Resume Analysis:
    {resume_analysis}

    GitHub Raw Data:
    {github_info}

    OUTPUT:
    Return ONLY one JSON object in the following structure:

    {{
    "github_analysis": <GitHub Analysis Object>,
    "final_analysis": <Final Analysis Object>
    }}
    Note: Provide a comprehensive analysis based on the inputs. Generate the timestamp as the current UTC time in ISO format (e.g., "2023-10-01T12:00:00Z").
    """

    response = model.generate_content(prompt)
    print(f"\nFinal Analysis completed!!")

    response_text = response.text.strip()
    if response_text.startswith("```json") and response_text.endswith("```"):
        response_text = response_text[7:-3].strip()  # Remove ```json and ```
    print(response_text)
    return response_text
