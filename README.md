# AI-Powered Resume Parser API ![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

This project is a FastAPI-based web service that intelligently parses resumes. It accepts resume files in PDF, DOC, or DOCX format, extracts the text, and utilizes Google's Gemini AI to analyze the content and return a structured JSON object containing the candidate's details.

## Features

- **File Upload:** Supports `.pdf`, `.doc`, and `.docx` file formats.
- **Text Extraction:** Efficiently scrapes text from various resume layouts.
- **AI-Powered Analysis:** Uses Google Gemini to understand and structure the unstructured text from resumes.
- **Structured JSON Output:** Provides a clean, predictable JSON response with personal information, education, work experience, skills, and more.

## Tech Stack

- **Backend:** Python, FastAPI
- **AI:** Google Gemini
- **File Parsing:** `PyPDF2`, `python-docx`
- **Server:** Uvicorn

## Project Structure

```
.
├── .env                # Environment variables (needs to be created)
├── main.py             # Main application file with FastAPI logic
├── requirements.txt    # Project dependencies
└── venv/               # Virtual environment directory
```

## Getting Started

Follow these instructions to get the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8+
- A Google API key for Gemini. You can get one from Google AI Studio.

### Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd ai-candidate-analysis
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    It's a good practice to have a `requirements.txt` file. You can create one with the necessary packages:

    ```
    fastapi
    uvicorn[standard]
    python-dotenv
    google-generativeai
    PyPDF2
    python-docx
    ```

    Then install them:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a file named `.env` in the root directory of the project and add your Google API key:
    ```.env
    GOOGLE_API_KEY="your_google_api_key_here"
    ```

### Running the Application

1.  **Start the server:**
    With the virtual environment activated, run the following command from the project's root directory:

    ```bash
    uvicorn main:app --reload
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

### Upload and Analyze a Resume

- **Endpoint:** `POST /analyze`
- **Description:** Upload a resume file for analysis.
- **Request:** `multipart/form-data` with a `file` field containing the resume and a `githubUserName` field for the candidate's GitHub username.

**Example using `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
     -F "file=@/path/to/your/resume.pdf" \
     -F "githubUserName=octocat"
```

You will receive a JSON response containing the parsed information from the resume.
