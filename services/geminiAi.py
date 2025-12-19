from config.settings import GOOGLE_API_KEY
import google.generativeai as genai
import asyncio
import re
import json


def clean_json_response(response_text: str) -> str:
    """Clean and extract valid JSON from LLM response."""
    response_text = response_text.strip()

    # Remove markdown code blocks
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    # Find JSON object boundaries
    json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(0)

    # Validate JSON
    try:
        json.loads(response_text)
        return response_text
    except json.JSONDecodeError as e:
        print(f"JSON validation error: {e}")
        print(f"Problematic response: {response_text[:500]}...")
        raise ValueError(f"Invalid JSON response from LLM: {e}")


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
    You are an expert GitHub profile analyzer. Analyze the provided GitHub user data and return ONLY a valid JSON object.
    
    IMPORTANT: 
    - Return ONLY valid JSON, no explanations or markdown
    - Use double quotes for all strings
    - Do not include any text before or after the JSON object
    - Ensure all JSON syntax is correct
    
    Input: {data}
    
    Output format (return ONLY this JSON structure):
    {{
    "summary": "string",
    "skills_inferred": ["string"],
    "activity_level": "string",
    "top_repositories": [
        {{
            "name": "string",
            "description": "string",
            "commits_count": 0,
            "last_commit_date": "string"
        }}
    ],
    "commit_patterns": "string",
    "languages_used": ["string"],
    "overall_rating": "string"
    }}
    """

    response = model.generate_content(prompt)
    print(f"\nGitHub Analysis completed!!")

    return clean_json_response(response.text)


async def analyze_github(data: dict) -> str:
    """Async wrapper that runs blocking Gemini call in thread pool."""
    return await asyncio.to_thread(_analyze_github_sync, data)


async def final_analysis(resume_text: str, github_analysis: dict) -> str:
    """Async wrapper that runs blocking Gemini call in thread pool."""
    return await asyncio.to_thread(_final_analysis_sync, resume_text, github_analysis)


def _final_analysis_sync(resume_text: str, github_analysis: dict) -> str:
    """Blocking final analysis function to run in thread pool."""
    print("Initializing final analysis...Waiting for response...")

    model = setup_gemini()

    prompt = f"""
    You are an expert candidate analyzer. Analyze the provided resume text and GitHub analysis, then return ONLY a valid JSON object.
    
    IMPORTANT: 
    - Return ONLY valid JSON, no explanations or markdown
    - Use double quotes for all strings
    - Do not include any text before or after the JSON object
    - Ensure all JSON syntax is correct
    - Parse the resume text to extract candidate information
    
    Resume Text: {resume_text}
    
    GitHub Analysis: {github_analysis}
    
    Output format (return ONLY this JSON structure):
    {{
      "timestamp": "2023-10-01T12:00:00Z",
      "overall_credibility_score": 0,
      "detailed_scores": {{
        "technology_match_score": 0,
        "project_verification_score": 0,
        "activity_authenticity_score": 0,
        "experience_consistency_score": 0
      }},
      "resume_summary": {{
        "name": "string",
        "claimed_skills": ["string"],
        "projects_mentioned": 0,
        "experience_years": 0,
        "education": ["string"]
      }},
      "github_summary": {{
        "total_repositories": 0,
        "total_commits": 0,
        "languages_used": ["string"],
        "active_since": "string"
      }},
      "verification_results": {{
        "strengths": ["string"],
        "concerns": ["string"]
      }},
      "detailed_analysis": "string",
      "recommendations": ["string"]
    }}
    """

    response = model.generate_content(prompt)
    print(f"\nFinal Analysis completed!!")

    return clean_json_response(response.text)
