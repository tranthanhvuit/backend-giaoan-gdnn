from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import os
from io import BytesIO
from docx import Document
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chuyen-decuong-giaoan.onrender.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-docx")
async def generate_docx(file: UploadFile = File(...), loai: str = Form(...)):
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Tệp rỗng hoặc không hợp lệ")

        with open("temp_input.docx", "wb") as f:
            f.write(contents)

        # Tải nội dung đề cương
        doc = Document("temp_input.docx")
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

        prompt = f"Chuyển nội dung sau thành giáo án dạng bảng, phân biệt hoạt động của giáo viên và học sinh, theo mẫu giáo án {loai}:

{text}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        generated_text = response.choices[0].message["content"]

        # Tạo file Word từ output GPT
        output_doc = Document()
        output_doc.add_paragraph(generated_text)

        output_stream = BytesIO()
        output_doc.save(output_stream)
        output_stream.seek(0)

        return StreamingResponse(
            output_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=giao_an.docx"}
        )

    except Exception as e:
        print("Lỗi xử lý:", str(e))
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")