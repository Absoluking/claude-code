from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import pypdf

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件并提取文本内容"""
    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower()

    allowed_extensions = {'.md', '.pdf', '.txt'}
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型。支持的类型: {', '.join(allowed_extensions)}")

    # 保存文件
    file_path = Path("uploads") / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 提取文本
    if file_ext == '.pdf':
        extracted_text = extract_text_from_pdf(file_path)
    elif file_ext in {'.md', '.txt'}:
        extracted_text = extract_text_from_plain(file_path)
    else:
        extracted_text = ""

    return {
        "filename": file.filename,
        "file_path": str(file_path),
        "file_size": file_path.stat().st_size,
        "extracted_text": extracted_text,
        "content_type": file.content_type
    }

def extract_text_from_pdf(file_path: Path) -> str:
    """从 PDF 文件提取文本"""
    text = ""
    try:
        with open(file_path, "rb") as f:
            pdf_reader = pypdf.PdfReader(f)
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text += f"\n--- 第 {page_num} 页 ---\n{page.extract_text()}"
    except Exception as e:
        text = f"[提取 PDF 失败: {str(e)}]"
    return text

def extract_text_from_plain(file_path: Path) -> str:
    """从 Markdown 和 TXT 文件读取文本"""
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(file_path, "r", encoding='gbk') as f:
                return f.read()
        except Exception as e:
            return f"[读取文件失败: {str(e)}]"
    except Exception as e:
        return f"[读取文件失败: {str(e)}]"

@app.get("/")
def read_root():
    return {"message": "FastAPI 文件上传服务运行中"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
