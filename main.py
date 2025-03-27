from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from doc_parser import extract_text_from_docx
from gpt_handler import generate_giao_an
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate(file: UploadFile = File(...), loai: str = Form(...)):
    contents = await file.read()
    text = extract_text_from_docx(contents)
    giao_an = generate_giao_an(text, loai)
    return {"result": giao_an}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
