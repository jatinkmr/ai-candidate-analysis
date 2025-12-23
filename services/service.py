import json
import asyncio

from fastapi import HTTPException, UploadFile
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO

from services.geminiAi import analyze_resume, final_analysis
from services.gitHubAi import fetchGitHubIformation


def get_welcome_message():
    return "Welcome to the FastAPI server!"


def validate_file(file: UploadFile):
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


async def scrape_pdf(file: UploadFile) -> str:
    binary_data = await file.read()
    try:
        pdf_buffer = BytesIO(binary_data)
        reader = PdfReader(pdf_buffer)
        texts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text.strip())
        return "\n\n".join(texts)
    except Exception as e:
        # Handle cases where PyPDF2 might fail
        raise HTTPException(status_code=500, detail=f"Error processing PDF file: {e}")


async def scrape_doc(file: UploadFile) -> str:
    binary_data = await file.read()
    try:
        doc_buffer = BytesIO(binary_data)
        doc = Document(doc_buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing DOC/DOCX file: {e}"
        )
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text


async def upload_and_analysis(file, githubUserName: str):
    print("Receiving File...")
    validate_file(file)
    if file.filename.lower().endswith(".pdf"):
        file_type = "pdf"
        data = await scrape_pdf(file)
    elif file.filename.lower().endswith(".docx") or file.filename.lower().endswith(
        ".doc"
    ):
        file_type = "docx"
        data = await scrape_doc(file)

    if not data:
        raise HTTPException(status_code=400, detail="unable to scrape the data")

    print(
        f"{file_type} file recv successfully and the github username is: {githubUserName}"
    )

    words = data.split()
    preview = " ".join(words)

    print(f"Scraped data -> {preview}")
    print(f"Data scrapped successfully from {file.filename}. Going for analysis...")

    try:
        github_info, analysis_json_str = await asyncio.gather(
            fetchGitHubIformation(githubUserName), analyze_resume(data)
        )

        # Convert JSON string to dict
        analysis_dict = json.loads(analysis_json_str)

        # Final Analysis
        final_analysis_data = await final_analysis(analysis_dict, github_info)
        final_analysis_info  = json.loads(final_analysis_data)

        # Combine GitHub info and analysis dict
        combined_result = {
            "resume_analysis": analysis_dict,
            "github_user_info": github_info,
            "github_analysis_info": final_analysis_info["github_analysis"],
            "final_analysis_info": final_analysis_info["final_analysis"],
        }
        # Return combined dict
        return combined_result

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred during analysis: {e}"
        )
