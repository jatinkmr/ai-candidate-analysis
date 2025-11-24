from fastapi import FastAPI
from controllers.controller import router
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
