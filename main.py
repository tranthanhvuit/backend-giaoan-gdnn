from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
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
    allow_origins=[
        "https://chuyen-decuong-giaoan.onrender.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
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
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")

        # Ghi ra tệp tạm
        with open("temp.docx", "wb") as f:
            f.write(contents)

        # Gọi OpenAI hoặc xử lý
        # Kết quả: tạo file mới export và trả lại

        return FileResponse("output.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="giao_an.docx")
    except Exception as e:
        print("Lỗi khi xử lý file:", e)
        raise HTTPException(status_code=500, detail=str(e))
