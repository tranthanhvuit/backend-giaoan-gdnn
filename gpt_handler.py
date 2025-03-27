import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def generate_giao_an(decuong: str, loai: str) -> str:
    prompt = f"""Bạn là giảng viên dạy nghề. Hãy chuyển nội dung sau thành giáo án {loai.upper()} theo bảng, phân biệt rõ hoạt động của GIÁO VIÊN và HỌC SINH:

--- Nội dung đề cương ---
{decuong}
--- Hết ---

Trình bày giáo án theo dạng bảng Markdown gồm các cột: Thời gian | Hoạt động của giáo viên | Hoạt động của học sinh | Phương pháp | Phương tiện"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý tạo giáo án chuyên nghiệp."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        print("❌ Lỗi GPT:", e)
        return "Lỗi GPT: " + str(e)
