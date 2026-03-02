from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
from pathlib import Path
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
from openai import OpenAI

app = FastAPI(title="File Upload API", version="1.0.0")

# 初始化嵌入模型
embedding_model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

# 初始化 OpenAI 客户端（用于调用 LLM）
anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL", "http://127.0.0.1:8000/v1")
anthropic_auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN", "test-token-123")
anthropic_model = os.getenv("ANTHROPIC_MODEL", "glm-4.7-flash")

try:
    llm_client = OpenAI(
        api_key=anthropic_auth_token,
        base_url=anthropic_base_url
    )
    LLM_AVAILABLE = True
except Exception as e:
    print(f"Warning: Failed to initialize LLM client: {str(e)}")
    LLM_AVAILABLE = False

# 自定义内存向量存储
class MemoryVectorStore:
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.metadatas = []

    def add(self, documents: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """添加文档到向量存储"""
        self.documents.extend(documents)
        self.embeddings.extend(embeddings)
        self.metadatas.extend(metadatas)

    def query(self, query_embedding: List[float], n_results: int = 3) -> Dict[str, List[List[str]]]:
        """执行语义搜索"""
        if not self.embeddings:
            return {"documents": [], "metadatas": [], "distances": [], "ids": []}

        # 计算余弦相似度
        query_array = np.array([query_embedding])
        doc_array = np.array(self.embeddings)

        # 计算点积（对于已归一化的向量，点积等于余弦相似度）
        dot_products = np.dot(doc_array, query_array[0])

        # 获取最相似的结果
        top_indices = np.argsort(dot_products)[-n_results:][::-1]

        results = {
            "documents": [self.documents[i] for i in top_indices],
            "metadatas": [self.metadatas[i] for i in top_indices],
            "distances": [1 - dot_products[i] for i in top_indices],  # 转换为距离
            "ids": [str(i) for i in top_indices]
        }

        return results

# 初始化内存向量存储
vector_store = MemoryVectorStore()

# 确保上传目录存在
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 挂载上传目录（可选）
# app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
async def root():
    return {
        "message": "FastAPI File Upload Service",
        "endpoints": ["/upload", "/ask"],
        "note": "Upload a text/PDF file using POST /upload, then ask questions using POST /ask"
    }


@app.get("/health")
async def health():
    """
    健康检查端点

    Returns:
        服务状态、向量存储状态和 LLM 状态
    """
    try:
        # 检查向量存储状态
        status = "healthy"
        docs_count = len(vector_store.documents)

        health_info = {
            "status": status,
            "collections": 1,  # 模拟值，因为使用自定义存储
            "documents_in_store": docs_count,
            "llm_available": LLM_AVAILABLE
        }

        if LLM_AVAILABLE:
            health_info["llm_model"] = anthropic_model
            health_info["llm_base_url"] = anthropic_base_url

        return health_info
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    将文本按指定大小分块，每块之间有重叠

    Args:
        text: 输入文本
        chunk_size: 每块大小（字符数）
        overlap: 重叠字符数

    Returns:
        文本块列表
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传文件并返回提取的内容，同时创建向量索引

    - **file**: 上传的文件

    支持的文件类型: .pdf, .md, .txt
    上传后会自动：
    - 保存文件到 uploads 目录
    - 提取文本内容
    - 创建向量索引用于语义检索
    """
    # 验证文件扩展名
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # 支持的文件类型
    allowed_extensions = {'.md', '.pdf', '.txt'}
    file_ext = Path(filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Only {', '.join(allowed_extensions)} are allowed"
        )

    # 保存文件到 uploads 目录
    file_path = UPLOAD_DIR / filename

    try:
        # 读取上传的文件内容
        content = await file.read()

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)

        # 根据文件类型提取文本
        text_content = None
        chunks = []

        if file_ext == '.pdf':
            # 使用 pypdf 提取 PDF 文本
            text_content = extract_text_from_pdf(file_path)
        elif file_ext == '.md' or file_ext == '.txt':
            # 直接读取文本文件
            text_content = content.decode('utf-8')

        # 创建向量索引（如果存在文本内容）
        if text_content:
            chunks = chunk_text(text_content)
            try:
                vectors = embedding_model.encode(chunks).tolist()
                vector_store.add(
                    documents=chunks,
                    embeddings=vectors,
                    metadatas=[{"source": filename, "chunk_index": idx} for idx in range(len(chunks))]
                )
            except Exception as e:
                # 向量存储失败不影响文件上传，只记录警告
                print(f"Warning: Failed to create vector index: {str(e)}")

        return {
            "filename": filename,
            "filepath": str(file_path),
            "file_size": len(content),
            "content": text_content if text_content else "",
            "chunks_count": len(chunks) if text_content else 0
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    使用 pypdf 提取 PDF 文本
    """
    try:
        reader = PdfReader(pdf_path)
        text_parts = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        return "\n\n".join(text_parts)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text from PDF: {str(e)}"
        )


@app.post("/ask")
async def ask_question(question: str):
    """
    基于向量检索和 LLM 生成答案

    - **question**: 用户问题

    该端点使用语义检索从已上传的文件中找到最相关的上下文，然后调用 LLM 生成自然语言答案。
    """
    try:
        # 1. 验证输入
        if not question or not question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )

        # 2. 检查 LLM 是否可用
        if not LLM_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="LLM service is not available. Please check ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN environment variables."
            )

        # 3. 将问题向量化
        query_embedding = embedding_model.encode(question).tolist()

        # 4. 在向量存储中查询最相关的 3 个文本块
        results = vector_store.query(query_embedding=query_embedding, n_results=3)

        # 5. 检查是否有结果
        if not results['documents'] or not results['documents'][0]:
            raise HTTPException(
                status_code=404,
                detail="No documents found in the vector store. Please upload a file first."
            )

        # 6. 构建提示词（RAG 提示词）
        context_parts = []
        for i, doc in enumerate(results['documents'][0], 1):
            context_parts.append(f"Reference {i}:\n{doc}\n")

        context_text = "\n---\n\n".join(context_parts)

        prompt = f"""你是一个智能问答助手。请基于以下上下文信息回答用户的问题。

上下文信息：
{context_text}

用户问题：{question}

请根据上下文信息给出准确、简洁的答案。如果上下文中没有相关信息，请明确说明。"""

        # 7. 调用 LLM 生成答案
        try:
            response = llm_client.chat.completions.create(
                model=anthropic_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的智能问答助手，能够基于提供的上下文信息准确回答问题。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1024,
                stream=False
            )

            # 8. 提取答案
            answer = response.choices[0].message.content

            return {
                "question": question,
                "answer": answer,
                "model": anthropic_model
            }

        except Exception as llm_error:
            raise HTTPException(
                status_code=500,
                detail=f"LLM API call failed: {str(llm_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
