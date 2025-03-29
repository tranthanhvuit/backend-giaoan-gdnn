from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import uuid
from docx import Document
import openai

# Load môi trường
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://giaoan-gdnn-ai.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_docx(file_bytes):
    from io import BytesIO
    doc = Document(BytesIO(file_bytes))
    full_text = [para.text for para in doc.paragraphs]
    return "\n".join(full_text)

def generate_giao_an(decuong_text, loai):
    prompt = f"""Chuyển nội dung đề cương sau thành giáo án dạng bảng theo mẫu của Tổng cục Giáo dục nghề nghiệp (phân biệt rõ hoạt động giáo viên - người học). 
Loại giáo án: {loai.upper()}
---
{decuong_text}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )
    return response['choices'][0]['message']['content']

@app.post("/generate")
async def generate(file: UploadFile = File(...), loai: str = Form(...)):
    content = await file.read()
    decuong_text = read_docx(content)
    result = generate_giao_an(decuong_text, loai)
    return {"result": result}

@app.post("/generate-docx")
async def generate_docx(file: UploadFile = File(...), loai: str = Form(...)):
    content = await file.read()
    decuong_text = read_docx(content)
    result = generate_giao_an(decuong_text, loai)

    filename = f"giaoan_{uuid.uuid4().hex}.docx"
    filepath = os.path.join("output", filename)
    os.makedirs("output", exist_ok=True)

    doc = Document()
    doc.add_heading("Giáo Án", 0)
    for line in result.split("\n"):
        doc.add_paragraph(line)
    doc.save(filepath)

    return FileResponse(
        path=filepath,
        filename="giao_an_output.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
