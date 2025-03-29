from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import os
from io import BytesIO
from docx import Document
import openai

# Load môi trường
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
@app.get("/")
def root():
    return {"message": "Backend is running"}

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Có thể thay bằng ["https://giaoan-gdnn-ai.vercel.app"] nếu cần hạn chế
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_docx(file_bytes):
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
    print(f"📥 Nhận file: {file.filename}, loại giáo án: {loai}")

    contents = await file.read()
    text = read_docx(contents)

    prompt = f"""Chuyển nội dung đề cương sau thành giáo án dạng bảng theo mẫu của Tổng cục Giáo dục nghề nghiệp (phân biệt rõ hoạt động giáo viên - người học). 
Loại giáo án: {loai.upper()}
---
{text}
"""

    print(f"🧠 Prompt gửi đến OpenAI:\n{prompt[:500]}...")  # Giới hạn để tránh log quá dài

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )

    result_text = response['choices'][0]['message']['content']
    print("✅ GPT trả về nội dung")

    word_doc = Document()
    word_doc.add_paragraph(result_text)
    buffer = BytesIO()
    word_doc.save(buffer)
    buffer.seek(0)

    print("📤 Trả về file Word thành công.")
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
        "Content-Disposition": "attachment; filename=giao_an_output.docx"
    })
