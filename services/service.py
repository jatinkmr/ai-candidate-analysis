import json

from fastapi import HTTPException, UploadFile
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO

from services.geminiAi import analyze_github, final_analysis
from services.gitHubAi import fetchGitHubIformation


def get_welcome_message():
    return "Welcome to the FastAPI server!"


def validate_file(file: UploadFile):
    """Validate file type and extension."""
    allowed_extensions = [".pdf", ".doc", ".docx"]
    allowed_content_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400, detail="Only PDF, DOC, or DOCX files are allowed."
        )

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF, DOC, or DOCX files are allowed.",
        )


async def validate_file_size(file: UploadFile) -> bytes:
    """Validate file size and return file content."""
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

    binary_data = await file.read()
    file_size = len(binary_data)

    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty. Please upload a valid resume.",
        )

    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File size ({size_mb:.2f}MB) exceeds the maximum allowed size of 10MB.",
        )

    return binary_data


def validate_resume_content(text: str, min_words: int = 50):
    """Validate that extracted text looks like a resume."""
    if not text or not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Unable to extract text from the file. The file might be empty or corrupted.",
        )

    # Check minimum word count
    words = text.split()
    word_count = len(words)

    if word_count < min_words:
        raise HTTPException(
            status_code=400,
            detail=f"The file contains only {word_count} words. This doesn't appear to be a valid resume. Please upload a proper resume document.",
        )

    # Check for common resume keywords (at least one should be present)
    resume_keywords = [
        "experience",
        "education",
        "skills",
        "work",
        "employment",
        "university",
        "college",
        "degree",
        "project",
        "qualification",
        "professional",
        "certification",
        "job",
        "career",
        "resume",
        "cv",
        "profile",
        "summary",
        "objective",
    ]

    text_lower = text.lower()
    has_resume_keyword = any(keyword in text_lower for keyword in resume_keywords)

    if not has_resume_keyword:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file doesn't appear to be a resume. Please upload a valid resume containing information about education, skills, or work experience.",
        )


async def scrape_pdf(binary_data: bytes) -> str:
    """Extract text from PDF file."""
    try:
        pdf_buffer = BytesIO(binary_data)
        reader = PdfReader(pdf_buffer)

        if len(reader.pages) == 0:
            raise HTTPException(status_code=400, detail="The PDF file has no pages.")

        texts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text.strip())

        extracted_text = "\n\n".join(texts)

        # Validate extracted content
        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Unable to extract meaningful text from the PDF. The file might be image-based or corrupted.",
            )

        return extracted_text
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing PDF file: {str(e)}"
        )


async def scrape_doc(binary_data: bytes) -> str:
    """Extract text from DOC/DOCX file."""
    try:
        doc_buffer = BytesIO(binary_data)
        doc = Document(doc_buffer)

        if len(doc.paragraphs) == 0:
            raise HTTPException(status_code=400, detail="The document has no content.")

        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"

        # Validate extracted content
        if not text or len(text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Unable to extract meaningful text from the document. The file might be empty or corrupted.",
            )

        return text.strip()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing DOC/DOCX file: {str(e)}"
        )


async def upload_and_analysis(file, githubUserName: str):
    """Main function to handle file upload and analysis."""
    print("Receiving File...")

    # Step 1: Validate file type
    validate_file(file)

    # Step 2: Validate file size and get binary data
    binary_data = await validate_file_size(file)

    # Step 3: Extract text from resume based on file type
    if file.filename.lower().endswith(".pdf"):
        file_type = "pdf"
        data = await scrape_pdf(binary_data)
    elif file.filename.lower().endswith(".docx") or file.filename.lower().endswith(
        ".doc"
    ):
        file_type = "docx"
        data = await scrape_doc(binary_data)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Step 4: Validate resume content (do this BEFORE fetching GitHub data)
    validate_resume_content(data)

    print(f"{file_type} file validated successfully!")
    print(f"Resume preview: {' '.join(data.split()[:100])}...")

    # Step 5: Now fetch GitHub information (only if resume is valid)
    print(f"Fetching GitHub information for: {githubUserName}...")
    github_info = await fetchGitHubIformation(githubUserName)

    print(f"Starting AI analysis...")

    try:
        githubAnalysis = await analyze_github(github_info)

        try:
            github_analysis_info = json.loads(githubAnalysis)
        except json.JSONDecodeError as e:
            print(f"Error parsing GitHub analysis JSON: {e}")
            print(f"GitHub analysis response: {githubAnalysis[:500]}...")
            raise HTTPException(
                status_code=500, detail=f"Failed to parse GitHub analysis: {str(e)}"
            )

        # Final Analysis with raw resume text
        final_analysis_data = await final_analysis(data, github_analysis_info)

        try:
            final_analysis_info = json.loads(final_analysis_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing final analysis JSON: {e}")
            print(f"Final analysis response: {final_analysis_data[:500]}...")
            raise HTTPException(
                status_code=500, detail=f"Failed to parse final analysis: {str(e)}"
            )

        # Combine GitHub info and analysis
        combined_result = {
            "github_user_info": github_info,
            "github_analysis_info": github_analysis_info,
            "final_analysis_info": final_analysis_info,
        }

        print("Analysis completed successfully!")
        return combined_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred during analysis: {e}"
        )
