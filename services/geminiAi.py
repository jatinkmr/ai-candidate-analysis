import os
import google.generativeai as genai


def setup_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


async def analyze_resume(text: str) -> str:
    print("Initializing analysis...Waiting for response...")

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
    print(f"\nAnalysis completed!!")

    response_text = response.text.strip()
    if response_text.startswith("```json") and response_text.endswith("```"):
        response_text = response_text[7:-3].strip()  # Remove ```json and ```

    return response_text
