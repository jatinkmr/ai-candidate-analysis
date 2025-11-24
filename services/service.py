from fastapi import HTTPException, UploadFile
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO

from services.geminiAi import analyze_text


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


def scrape_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file,"rb")
    texts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texts.append(page_text.strip())
    return "\\n\\n".join(texts)

# async def scrape_pdf(file: UploadFile) -> str:
#     binaryData =  await file.read()
#     # extracted_content = extract_pdf_text(binary_data)
#     try:
#         # Load binary data into buffer
#         pdf_buffer = BytesIO(binaryData)
#         reader = PdfReader(pdf_buffer)

#         extracted_text = []

#         for page_num, page in enumerate(reader.pages):
#             try:
#                 text = page.extract_text()  # PyPDF2 extraction
#                 if text:
#                     # Clean & preserve formatting
#                     text = text.replace("\u00A0", " ").strip()
#                     extracted_text.append(f"--- Page {page_num + 1} ---\n{text}\n")
#                 else:
#                     extracted_text.append(f"--- Page {page_num + 1}: (No extractable text found) ---\n")
#             except Exception as e:
#                 extracted_text.append(f"--- Page {page_num + 1}: Error extracting text: {str(e)} ---\n")

#         return "\n".join(extracted_text).strip()

#     except Exception as e:
#         return f"[ERROR] Unable to read PDF file: {str(e)}"


def scrape_doc(file: UploadFile) -> str:
    doc = Document(file.file)
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text


async def upload_and_analysis(file):
    print("Receiving File...")
    validate_file(file)
    if file.filename.lower().endswith(".pdf"):
        file_type = "pdf"
        data = await scrape_pdf(file)
    elif file.filename.lower().endswith(".docx") or file.filename.lower().endswith(
        ".doc"
    ):
        file_type = "docx"
        data = scrape_doc(file)

    if not data:
        raise HTTPException(status_code=400, detail="unable to scrape the data")

    print(f"{file_type} file recv successfully!!")
    # Print only the first 1000 words of the scraped data
    words = data.split()
    preview = " ".join(words)
    # if len(words) > 1000:
    #     preview += " ..."
    print(f"Scraped data -> {preview}")
    print(f"Data scrapped successfully from {file.filename}. Going for analysis...")

    try:
        return analyze_text(data)
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred during analysis: {e}"
        )
