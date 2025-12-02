# AI-Powered Candidate Analysis API ![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

This project is a FastAPI-based web service that intelligently analyzes a candidate's profile using their resume and GitHub profile. It accepts a resume file (PDF, DOC, or DOCX) and a GitHub username, extracts text from the resume, fetches the user's GitHub data, and then utilizes Google's Gemini AI to analyze both sources of information. The result is a structured JSON object containing a comprehensive analysis of the candidate's skills, experience, and online presence.

## Features

- **File Upload:** Supports `.pdf`, `.doc`, and `.docx` file formats for resumes.
- **Text Extraction:** Efficiently scrapes text from various resume layouts.
- **GitHub Integration:** Fetches user information, repositories, and commit history from GitHub.
- **AI-Powered Analysis:** Uses Google Gemini to:
    - Parse and structure information from resumes.
    - Analyze GitHub profiles for skills, activity, and contribution patterns.
    - Perform a final, consolidated analysis of the candidate based on both their resume and GitHub profile.
- **Structured JSON Output:** Provides a clean, predictable JSON response with personal information, education, work experience, skills, GitHub analysis, and a final overall assessment.

## Tech Stack

- **Backend:** Python, FastAPI
- **AI:** Google Gemini
- **File Parsing:** `PyPDF2`, `python-docx`
- **GitHub API:** `PyGithub`
- **Server:** Uvicorn

## Project Structure

```
.
├── .env.example        # Example environment variables
├── main.py             # Main FastAPI application entrypoint
├── requirements.txt    # Project dependencies
├── config/             # Configuration settings
│   └── settings.py
├── controllers/        # API route handlers
│   └── controller.py
├── services/           # Business logic and service layer
│   ├── geminiAi.py
│   ├── gitHubAi.py
│   └── service.py
└── .venv/              # Virtual environment directory
```

## Getting Started

Follow these instructions to get the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8+
- A Google API key for Gemini. You can get one from [Google AI Studio](https://aistudio.google.com/).
- A GitHub Personal Access Token with `repo` scope. You can create one [here](https://github.com/settings/tokens).

### Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd ai-candidate-analysis
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate

    # For Windows
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a file named `.env` in the root directory by copying the example file:
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file and add your API keys:
    ```.env
    GOOGLE_API_KEY="your_google_api_key_here"
    Github_Access_Token="your_github_access_token_here"
    ```

### Running the Application

1.  **Start the server:**
    With the virtual environment activated, run the following command from the project's root directory:

    ```bash
    python main.py
    ```

2.  **Access the API:**
    The application will be running at `http://127.0.0.1:8000`.

## API Usage

### Interactive API Docs (Swagger UI)

Once the server is running, you can access the interactive API documentation by navigating to `http://127.0.0.1:8000/docs` in your web browser.

This Swagger UI allows you to:

- View all available API endpoints.
- See the expected request and response models.
- Test the endpoints directly from your browser.

### Upload and Analyze a Candidate

- **Endpoint:** `POST /analyze`
- **Description:** Upload a resume file and provide a GitHub username for a comprehensive analysis.
- **Request:** `multipart/form-data` with a `file` field containing the resume and a `githubUserName` field for the candidate's GitHub username.

**Example using `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
     -F "file=@/path/to/your/resume.pdf" \
     -F "githubUserName=octocat"
```

You will receive a JSON response containing the parsed information from the resume, an analysis of the GitHub profile, and a final consolidated analysis.

```