import json
from fastapi import APIRouter, status, Response, UploadFile, File, Form
from services.service import get_welcome_message, upload_and_analysis

router = APIRouter()


@router.get("/")
def home():
    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps({"message": get_welcome_message()}),
        media_type="application/json",
    )


@router.post("/analyze")
async def upload_file(file: UploadFile = File(...), githubUserName: str = Form(...)):
    response_data = await upload_and_analysis(file, githubUserName)
    try:
        response_json = json.loads(response_data)
    except json.JSONDecodeError:
        response_json = response_data

    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(
            {
                "message": f"File '{file.filename}' uploaded, scraped & analysis successfully.",
                "response": response_json,
            }
        ),
        media_type="application/json",
    )
